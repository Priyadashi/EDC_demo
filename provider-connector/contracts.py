"""
Contract Negotiation API for Provider Connector

Implements the Contract Negotiation Protocol from the Dataspace Protocol.
Handles the complete negotiation lifecycle from request to finalization.
"""

import sys
import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.policies import POLICY_TEMPLATES, PolicyEvaluator, get_policy_description
from store import (
    get_store, get_asset_by_id, get_negotiation, save_negotiation,
    get_agreement, save_agreement, log_event
)

router = APIRouter()
policy_evaluator = PolicyEvaluator()


class NegotiationRequest(BaseModel):
    """Request to initiate a contract negotiation."""
    consumer_id: str
    asset_id: str
    consumer_attributes: Optional[dict] = None
    callback_address: Optional[str] = None


class NegotiationAction(BaseModel):
    """Action on a negotiation (offer, agree, verify, etc.)."""
    consumer_attributes: Optional[dict] = None


@router.get("")
@router.get("/")
async def list_negotiations():
    """List all negotiations."""
    store = get_store()
    negotiations = list(store.get("negotiations", {}).values())

    return {
        "negotiations": [
            {
                "id": n["id"],
                "state": n["state"],
                "asset_id": n["asset_id"],
                "consumer_id": n["consumer_id"],
                "created_at": n["created_at"],
                "updated_at": n["updated_at"]
            }
            for n in negotiations
        ],
        "total": len(negotiations)
    }


@router.post("")
@router.post("/")
async def initiate_negotiation(request: NegotiationRequest):
    """
    Initiate a new contract negotiation.

    The consumer requests access to a dataset. The provider evaluates
    the request against the dataset's policy and either offers a contract
    or rejects the request.
    """
    # Verify asset exists
    asset = get_asset_by_id(request.asset_id)
    if not asset:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "ASSET_NOT_FOUND",
                "message": f"Asset '{request.asset_id}' not found"
            }
        )

    # Get policy for this asset
    policy_id = asset.get("policy_id", "open-access")
    policy = POLICY_TEMPLATES.get(policy_id)

    if not policy:
        raise HTTPException(
            status_code=500,
            detail={"error": "POLICY_NOT_FOUND", "message": f"Policy '{policy_id}' not configured"}
        )

    # Create negotiation record
    negotiation_id = f"negotiation-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    negotiation = {
        "id": negotiation_id,
        "state": "REQUESTED",
        "provider_id": "provider-automotors-oem",
        "consumer_id": request.consumer_id,
        "asset_id": request.asset_id,
        "policy_id": policy_id,
        "consumer_attributes": request.consumer_attributes or {},
        "callback_address": request.callback_address,
        "created_at": now,
        "updated_at": now,
        "state_history": [
            {"state": "REQUESTED", "timestamp": now, "actor": request.consumer_id}
        ]
    }

    save_negotiation(negotiation)
    log_event("NEGOTIATION_INITIATED", {
        "negotiation_id": negotiation_id,
        "consumer_id": request.consumer_id,
        "asset_id": request.asset_id
    })

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:ContractNegotiation",
        "@id": negotiation_id,
        "dspace:state": "REQUESTED",
        "dspace:providerPid": "provider-automotors-oem",
        "dspace:consumerPid": request.consumer_id,
        "asset_id": request.asset_id,
        "policy": {
            "id": policy.id,
            "description": get_policy_description(policy)
        },
        "message": "Negotiation initiated. Provider will evaluate your request.",
        "next_action": "POST /api/negotiations/{id}/offer to receive provider's offer"
    }


@router.get("/{negotiation_id}")
async def get_negotiation_status(negotiation_id: str):
    """Get the current status of a negotiation."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(
            status_code=404,
            detail={"error": "NEGOTIATION_NOT_FOUND", "message": f"Negotiation '{negotiation_id}' not found"}
        )

    asset = get_asset_by_id(negotiation["asset_id"])
    policy = POLICY_TEMPLATES.get(negotiation.get("policy_id", "open-access"))

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:ContractNegotiation",
        "@id": negotiation["id"],
        "dspace:state": negotiation["state"],
        "dspace:providerPid": negotiation["provider_id"],
        "dspace:consumerPid": negotiation["consumer_id"],
        "asset": {
            "id": asset["id"] if asset else negotiation["asset_id"],
            "name": asset["name"] if asset else "Unknown"
        },
        "policy": {
            "id": policy.id if policy else negotiation.get("policy_id"),
            "description": get_policy_description(policy) if policy else "Unknown"
        },
        "state_history": negotiation.get("state_history", []),
        "agreement_id": negotiation.get("agreement_id"),
        "created_at": negotiation["created_at"],
        "updated_at": negotiation["updated_at"]
    }


@router.post("/{negotiation_id}/offer")
async def provider_offer(negotiation_id: str, action: NegotiationAction = None):
    """
    Provider sends an offer to the consumer.

    The provider evaluates the consumer's attributes against the policy
    and either makes an offer (if policy allows) or terminates.
    """
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    if negotiation["state"] != "REQUESTED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Cannot offer in state '{negotiation['state']}'. Expected 'REQUESTED'."
            }
        )

    # Get policy and evaluate
    policy = POLICY_TEMPLATES.get(negotiation.get("policy_id", "open-access"))
    consumer_attrs = action.consumer_attributes if action else negotiation.get("consumer_attributes", {})

    # Evaluate policy
    result = policy_evaluator.evaluate(policy, consumer_attrs)

    now = datetime.utcnow().isoformat()

    if result.allowed:
        # Policy allows access - make offer
        negotiation["state"] = "OFFERED"
        negotiation["updated_at"] = now
        negotiation["state_history"].append({
            "state": "OFFERED",
            "timestamp": now,
            "actor": "provider-automotors-oem",
            "policy_evaluation": "PASSED"
        })
        negotiation["policy_evaluation"] = {
            "allowed": True,
            "evaluated_constraints": result.evaluated_constraints
        }

        save_negotiation(negotiation)
        log_event("OFFER_MADE", {"negotiation_id": negotiation_id})

        return {
            "@context": {"@vocab": "https://w3id.org/dspace/"},
            "@type": "dspace:ContractOfferMessage",
            "dspace:providerPid": negotiation["provider_id"],
            "dspace:consumerPid": negotiation["consumer_id"],
            "dspace:state": "OFFERED",
            "policy_evaluation": {
                "result": "ALLOWED",
                "reason": result.reason,
                "constraints_checked": result.evaluated_constraints
            },
            "message": "Policy evaluation passed. Offer made to consumer.",
            "next_action": "POST /api/negotiations/{id}/agree to accept the offer"
        }
    else:
        # Policy denies access - terminate negotiation
        negotiation["state"] = "TERMINATED"
        negotiation["updated_at"] = now
        negotiation["state_history"].append({
            "state": "TERMINATED",
            "timestamp": now,
            "actor": "provider-automotors-oem",
            "policy_evaluation": "FAILED",
            "reason": result.reason
        })
        negotiation["policy_evaluation"] = {
            "allowed": False,
            "reason": result.reason,
            "evaluated_constraints": result.evaluated_constraints
        }

        save_negotiation(negotiation)
        log_event("NEGOTIATION_TERMINATED", {
            "negotiation_id": negotiation_id,
            "reason": result.reason
        })

        return {
            "@context": {"@vocab": "https://w3id.org/dspace/"},
            "@type": "dspace:ContractNegotiationTerminationMessage",
            "dspace:providerPid": negotiation["provider_id"],
            "dspace:consumerPid": negotiation["consumer_id"],
            "dspace:state": "TERMINATED",
            "policy_evaluation": {
                "result": "DENIED",
                "reason": result.reason,
                "constraints_checked": result.evaluated_constraints
            },
            "message": "Policy evaluation failed. Negotiation terminated.",
            "hint": "Check the constraints_checked to understand which requirements were not met."
        }


@router.post("/{negotiation_id}/agree")
async def consumer_agree(negotiation_id: str):
    """
    Consumer agrees to the offer.

    After the provider makes an offer, the consumer can agree to the terms.
    """
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    if negotiation["state"] != "OFFERED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Cannot agree in state '{negotiation['state']}'. Expected 'OFFERED'."
            }
        )

    now = datetime.utcnow().isoformat()
    negotiation["state"] = "AGREED"
    negotiation["updated_at"] = now
    negotiation["state_history"].append({
        "state": "AGREED",
        "timestamp": now,
        "actor": negotiation["consumer_id"]
    })

    save_negotiation(negotiation)
    log_event("CONSUMER_AGREED", {"negotiation_id": negotiation_id})

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:ContractAgreementMessage",
        "dspace:providerPid": negotiation["provider_id"],
        "dspace:consumerPid": negotiation["consumer_id"],
        "dspace:state": "AGREED",
        "message": "Consumer has agreed to the offer. Proceeding to verification.",
        "next_action": "POST /api/negotiations/{id}/verify to verify the agreement"
    }


@router.post("/{negotiation_id}/verify")
async def verify_agreement(negotiation_id: str):
    """
    Verify the agreement.

    Both parties verify the terms before finalization.
    """
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    if negotiation["state"] != "AGREED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Cannot verify in state '{negotiation['state']}'. Expected 'AGREED'."
            }
        )

    now = datetime.utcnow().isoformat()
    negotiation["state"] = "VERIFIED"
    negotiation["updated_at"] = now
    negotiation["state_history"].append({
        "state": "VERIFIED",
        "timestamp": now,
        "actor": "system"
    })

    save_negotiation(negotiation)
    log_event("AGREEMENT_VERIFIED", {"negotiation_id": negotiation_id})

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:ContractAgreementVerificationMessage",
        "dspace:providerPid": negotiation["provider_id"],
        "dspace:consumerPid": negotiation["consumer_id"],
        "dspace:state": "VERIFIED",
        "message": "Agreement verified by both parties.",
        "next_action": "POST /api/negotiations/{id}/finalize to finalize and create contract"
    }


@router.post("/{negotiation_id}/finalize")
async def finalize_agreement(negotiation_id: str):
    """
    Finalize the negotiation and create a contract agreement.

    This creates a binding agreement that authorizes data transfer.
    """
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    if negotiation["state"] != "VERIFIED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Cannot finalize in state '{negotiation['state']}'. Expected 'VERIFIED'."
            }
        )

    now = datetime.utcnow().isoformat()

    # Create agreement
    agreement_id = f"agreement-{uuid.uuid4().hex[:8]}"
    policy = POLICY_TEMPLATES.get(negotiation.get("policy_id", "open-access"))

    agreement = {
        "id": agreement_id,
        "negotiation_id": negotiation_id,
        "asset_id": negotiation["asset_id"],
        "policy_id": negotiation.get("policy_id"),
        "policy_description": get_policy_description(policy) if policy else "Unknown",
        "provider_id": negotiation["provider_id"],
        "consumer_id": negotiation["consumer_id"],
        "signing_date": now,
        "status": "ACTIVE"
    }

    save_agreement(agreement)

    # Update negotiation
    negotiation["state"] = "FINALIZED"
    negotiation["updated_at"] = now
    negotiation["agreement_id"] = agreement_id
    negotiation["state_history"].append({
        "state": "FINALIZED",
        "timestamp": now,
        "actor": "system",
        "agreement_id": agreement_id
    })

    save_negotiation(negotiation)
    log_event("AGREEMENT_FINALIZED", {
        "negotiation_id": negotiation_id,
        "agreement_id": agreement_id
    })

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:ContractNegotiationEventMessage",
        "dspace:providerPid": negotiation["provider_id"],
        "dspace:consumerPid": negotiation["consumer_id"],
        "dspace:state": "FINALIZED",
        "dspace:eventType": "FINALIZED",
        "agreement": {
            "id": agreement_id,
            "asset_id": agreement["asset_id"],
            "policy": agreement["policy_description"],
            "signing_date": agreement["signing_date"]
        },
        "message": "Contract agreement created. You can now initiate data transfer.",
        "next_action": "POST /api/transfers with agreement_id to start data transfer"
    }


@router.post("/{negotiation_id}/terminate")
async def terminate_negotiation(negotiation_id: str):
    """Terminate an active negotiation."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    if negotiation["state"] in ["FINALIZED", "TERMINATED"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Negotiation already in final state '{negotiation['state']}'"
            }
        )

    now = datetime.utcnow().isoformat()
    negotiation["state"] = "TERMINATED"
    negotiation["updated_at"] = now
    negotiation["state_history"].append({
        "state": "TERMINATED",
        "timestamp": now,
        "actor": "user",
        "reason": "User requested termination"
    })

    save_negotiation(negotiation)
    log_event("NEGOTIATION_TERMINATED", {"negotiation_id": negotiation_id, "reason": "User request"})

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:ContractNegotiationTerminationMessage",
        "dspace:providerPid": negotiation["provider_id"],
        "dspace:consumerPid": negotiation["consumer_id"],
        "dspace:state": "TERMINATED",
        "message": "Negotiation terminated."
    }


@router.get("/{negotiation_id}/history")
async def get_negotiation_history(negotiation_id: str):
    """Get the complete history of a negotiation."""
    negotiation = get_negotiation(negotiation_id)

    if not negotiation:
        raise HTTPException(status_code=404, detail={"error": "NEGOTIATION_NOT_FOUND"})

    return {
        "negotiation_id": negotiation_id,
        "current_state": negotiation["state"],
        "history": negotiation.get("state_history", []),
        "policy_evaluation": negotiation.get("policy_evaluation")
    }
