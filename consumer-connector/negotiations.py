"""
Contract Negotiation API for Consumer Connector

Initiates and manages contract negotiations with providers.
"""

import os
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from store import (
    get_identity, get_negotiation, save_negotiation,
    get_all_negotiations, save_agreement, log_event
)

router = APIRouter()

PROVIDER_URL = os.getenv("PROVIDER_URL", "http://localhost:8080")


class NegotiationRequest(BaseModel):
    """Request to start a negotiation."""
    asset_id: str
    use_identity: Optional[bool] = True  # Use stored identity attributes


class IdentityOverride(BaseModel):
    """Override identity for a specific negotiation."""
    partner_type: Optional[str] = None
    region: Optional[str] = None
    certifications: Optional[list[str]] = None
    purpose: Optional[str] = None


@router.get("")
@router.get("/")
async def list_negotiations():
    """List all negotiations initiated by this consumer."""
    negotiations = get_all_negotiations()

    return {
        "negotiations": [
            {
                "id": n["id"],
                "provider_negotiation_id": n.get("provider_negotiation_id"),
                "asset_id": n["asset_id"],
                "state": n["state"],
                "created_at": n["created_at"],
                "agreement_id": n.get("agreement_id")
            }
            for n in negotiations
        ],
        "total": len(negotiations)
    }


@router.post("")
@router.post("/")
async def initiate_negotiation(request: NegotiationRequest):
    """
    Initiate a contract negotiation with the provider.

    Uses the consumer's identity attributes for policy evaluation.
    """
    identity = get_identity()

    # Prepare consumer attributes for the provider
    consumer_attributes = {
        "partner_type": identity.get("partner_type"),
        "region": identity.get("region"),
        "certification": identity.get("certifications", []),
        "purpose": identity.get("purpose")
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/negotiations",
                json={
                    "consumer_id": identity["consumer_id"],
                    "asset_id": request.asset_id,
                    "consumer_attributes": consumer_attributes
                }
            )
            response.raise_for_status()
            provider_response = response.json()

        # Store local negotiation record
        provider_neg_id = provider_response.get("@id")
        now = datetime.utcnow().isoformat()

        negotiation = {
            "id": f"local-{provider_neg_id}",
            "provider_negotiation_id": provider_neg_id,
            "asset_id": request.asset_id,
            "state": "REQUESTED",
            "provider_state": provider_response.get("dspace:state"),
            "consumer_attributes": consumer_attributes,
            "created_at": now,
            "updated_at": now,
            "history": [
                {"action": "INITIATED", "timestamp": now, "response": provider_response}
            ]
        }

        save_negotiation(negotiation)
        log_event("NEGOTIATION_INITIATED", {
            "local_id": negotiation["id"],
            "provider_id": provider_neg_id,
            "asset_id": request.asset_id
        })

        return {
            "status": "initiated",
            "local_negotiation_id": negotiation["id"],
            "provider_negotiation_id": provider_neg_id,
            "asset_id": request.asset_id,
            "consumer_attributes": consumer_attributes,
            "provider_response": provider_response,
            "next_action": f"POST /api/negotiations/{negotiation['id']}/request-offer"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail={"error": "PROVIDER_UNREACHABLE", "message": f"Cannot connect to {PROVIDER_URL}"}
        )


@router.get("/{negotiation_id}")
async def get_negotiation_status(negotiation_id: str):
    """Get the current status of a negotiation."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(
            status_code=404,
            detail={"error": "NEGOTIATION_NOT_FOUND"}
        )

    # Optionally refresh from provider
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{PROVIDER_URL}/api/negotiations/{negotiation['provider_negotiation_id']}"
            )
            if response.status_code == 200:
                provider_status = response.json()
                negotiation["provider_state"] = provider_status.get("dspace:state")
                negotiation["provider_details"] = provider_status
    except Exception:
        pass  # Use cached state if provider unavailable

    return negotiation


@router.post("/{negotiation_id}/request-offer")
async def request_provider_offer(negotiation_id: str, override: IdentityOverride = None):
    """
    Request the provider to make an offer.

    The provider will evaluate our attributes against the dataset policy.
    """
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    # Prepare attributes (with optional overrides for demo)
    identity = get_identity()
    consumer_attrs = {
        "partner_type": override.partner_type if override and override.partner_type else identity.get("partner_type"),
        "region": override.region if override and override.region else identity.get("region"),
        "certification": override.certifications if override and override.certifications else identity.get("certifications", []),
        "purpose": override.purpose if override and override.purpose else identity.get("purpose")
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/negotiations/{negotiation['provider_negotiation_id']}/offer",
                json={"consumer_attributes": consumer_attrs}
            )
            provider_response = response.json()

        now = datetime.utcnow().isoformat()
        new_state = provider_response.get("dspace:state", "UNKNOWN")

        negotiation["state"] = new_state
        negotiation["provider_state"] = new_state
        negotiation["updated_at"] = now
        negotiation["policy_evaluation"] = provider_response.get("policy_evaluation")
        negotiation["history"].append({
            "action": "OFFER_REQUESTED",
            "timestamp": now,
            "attributes_sent": consumer_attrs,
            "response": provider_response
        })

        save_negotiation(negotiation)

        result = {
            "status": new_state,
            "negotiation_id": negotiation_id,
            "policy_evaluation": provider_response.get("policy_evaluation"),
            "message": provider_response.get("message")
        }

        if new_state == "OFFERED":
            result["next_action"] = f"POST /api/negotiations/{negotiation_id}/agree"
        elif new_state == "TERMINATED":
            result["hint"] = provider_response.get("hint", "Policy requirements not met")

        return result

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )


@router.post("/{negotiation_id}/agree")
async def agree_to_offer(negotiation_id: str):
    """Agree to the provider's offer."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    if negotiation["state"] != "OFFERED":
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_STATE", "message": f"Cannot agree in state '{negotiation['state']}'"}
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/negotiations/{negotiation['provider_negotiation_id']}/agree"
            )
            response.raise_for_status()
            provider_response = response.json()

        now = datetime.utcnow().isoformat()
        negotiation["state"] = "AGREED"
        negotiation["provider_state"] = provider_response.get("dspace:state")
        negotiation["updated_at"] = now
        negotiation["history"].append({
            "action": "AGREED",
            "timestamp": now,
            "response": provider_response
        })

        save_negotiation(negotiation)

        return {
            "status": "AGREED",
            "negotiation_id": negotiation_id,
            "message": provider_response.get("message"),
            "next_action": f"POST /api/negotiations/{negotiation_id}/verify"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )


@router.post("/{negotiation_id}/verify")
async def verify_agreement(negotiation_id: str):
    """Verify the agreement."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/negotiations/{negotiation['provider_negotiation_id']}/verify"
            )
            response.raise_for_status()
            provider_response = response.json()

        now = datetime.utcnow().isoformat()
        negotiation["state"] = "VERIFIED"
        negotiation["provider_state"] = provider_response.get("dspace:state")
        negotiation["updated_at"] = now
        negotiation["history"].append({
            "action": "VERIFIED",
            "timestamp": now,
            "response": provider_response
        })

        save_negotiation(negotiation)

        return {
            "status": "VERIFIED",
            "negotiation_id": negotiation_id,
            "message": provider_response.get("message"),
            "next_action": f"POST /api/negotiations/{negotiation_id}/finalize"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )


@router.post("/{negotiation_id}/finalize")
async def finalize_negotiation(negotiation_id: str):
    """Finalize the negotiation and receive the agreement."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/negotiations/{negotiation['provider_negotiation_id']}/finalize"
            )
            response.raise_for_status()
            provider_response = response.json()

        now = datetime.utcnow().isoformat()
        agreement_data = provider_response.get("agreement", {})
        agreement_id = agreement_data.get("id")

        # Store agreement locally
        if agreement_id:
            agreement = {
                "id": agreement_id,
                "negotiation_id": negotiation_id,
                "asset_id": agreement_data.get("asset_id"),
                "policy": agreement_data.get("policy"),
                "signing_date": agreement_data.get("signing_date"),
                "status": "ACTIVE"
            }
            save_agreement(agreement)

        negotiation["state"] = "FINALIZED"
        negotiation["provider_state"] = provider_response.get("dspace:state")
        negotiation["agreement_id"] = agreement_id
        negotiation["updated_at"] = now
        negotiation["history"].append({
            "action": "FINALIZED",
            "timestamp": now,
            "agreement": agreement_data,
            "response": provider_response
        })

        save_negotiation(negotiation)
        log_event("AGREEMENT_RECEIVED", {
            "negotiation_id": negotiation_id,
            "agreement_id": agreement_id
        })

        return {
            "status": "FINALIZED",
            "negotiation_id": negotiation_id,
            "agreement_id": agreement_id,
            "agreement": agreement_data,
            "message": "Contract finalized! You can now request data transfer.",
            "next_action": f"POST /api/transfers with agreement_id='{agreement_id}'"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )


@router.get("/{negotiation_id}/history")
async def get_negotiation_history(negotiation_id: str):
    """Get the complete history of a negotiation."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    return {
        "negotiation_id": negotiation_id,
        "current_state": negotiation["state"],
        "history": negotiation.get("history", []),
        "policy_evaluation": negotiation.get("policy_evaluation")
    }
