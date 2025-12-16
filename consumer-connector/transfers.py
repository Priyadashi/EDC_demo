"""
Transfer API for Consumer Connector

Initiates and manages data transfers from providers.
"""

import os
import httpx
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from store import (
    get_agreement, get_transfer, save_transfer,
    get_all_transfers, save_received_data, get_received_data,
    get_all_received_data, log_event
)

router = APIRouter()

PROVIDER_URL = os.getenv("PROVIDER_URL", "http://localhost:8080")


class TransferRequest(BaseModel):
    """Request to initiate a data transfer."""
    agreement_id: str


@router.get("")
@router.get("/")
async def list_transfers():
    """List all data transfers."""
    transfers = get_all_transfers()

    return {
        "transfers": [
            {
                "id": t["id"],
                "provider_transfer_id": t.get("provider_transfer_id"),
                "agreement_id": t["agreement_id"],
                "asset_id": t.get("asset_id"),
                "state": t["state"],
                "created_at": t["created_at"],
                "completed_at": t.get("completed_at"),
                "has_data": t.get("has_data", False)
            }
            for t in transfers
        ],
        "total": len(transfers)
    }


@router.post("")
@router.post("/")
async def initiate_transfer(request: TransferRequest):
    """
    Initiate a data transfer from the provider.

    Requires a valid agreement_id from a finalized contract.
    """
    # Verify we have this agreement
    agreement = get_agreement(request.agreement_id)

    if not agreement:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "AGREEMENT_NOT_FOUND",
                "message": f"Agreement '{request.agreement_id}' not found locally",
                "hint": "Complete a contract negotiation first"
            }
        )

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/transfers",
                json={"agreement_id": request.agreement_id}
            )
            response.raise_for_status()
            provider_response = response.json()

        provider_transfer_id = provider_response.get("@id")
        now = datetime.utcnow().isoformat()

        transfer = {
            "id": f"local-{provider_transfer_id}",
            "provider_transfer_id": provider_transfer_id,
            "agreement_id": request.agreement_id,
            "asset_id": agreement.get("asset_id"),
            "state": "REQUESTED",
            "provider_state": provider_response.get("dspace:state"),
            "created_at": now,
            "has_data": False,
            "history": [
                {"action": "INITIATED", "timestamp": now, "response": provider_response}
            ]
        }

        save_transfer(transfer)
        log_event("TRANSFER_INITIATED", {
            "local_id": transfer["id"],
            "provider_id": provider_transfer_id
        })

        return {
            "status": "initiated",
            "local_transfer_id": transfer["id"],
            "provider_transfer_id": provider_transfer_id,
            "asset_id": agreement.get("asset_id"),
            "message": provider_response.get("message"),
            "next_action": f"POST /api/transfers/{transfer['id']}/start"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail={"error": "PROVIDER_UNREACHABLE"}
        )


@router.get("/{transfer_id}")
async def get_transfer_status(transfer_id: str):
    """Get the current status of a transfer."""
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    return transfer


@router.post("/{transfer_id}/start")
async def start_transfer(transfer_id: str):
    """Start the data transfer."""
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/transfers/{transfer['provider_transfer_id']}/start"
            )
            response.raise_for_status()
            provider_response = response.json()

        now = datetime.utcnow().isoformat()
        transfer["state"] = "STARTED"
        transfer["provider_state"] = provider_response.get("dspace:state")
        transfer["started_at"] = now
        transfer["history"].append({
            "action": "STARTED",
            "timestamp": now,
            "response": provider_response
        })

        save_transfer(transfer)

        return {
            "status": "STARTED",
            "transfer_id": transfer_id,
            "message": provider_response.get("message"),
            "next_action": f"POST /api/transfers/{transfer_id}/complete"
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )


@router.post("/{transfer_id}/complete")
async def complete_transfer(transfer_id: str):
    """Complete the transfer and receive the data."""
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    try:
        # First, complete the transfer on the provider side
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{PROVIDER_URL}/api/transfers/{transfer['provider_transfer_id']}/complete"
            )
            response.raise_for_status()
            provider_response = response.json()

        # Then fetch the actual data
        async with httpx.AsyncClient(timeout=60.0) as client:
            data_response = await client.get(
                f"{PROVIDER_URL}/api/transfers/{transfer['provider_transfer_id']}/data"
            )
            data_response.raise_for_status()
            data_payload = data_response.json()

        now = datetime.utcnow().isoformat()

        # Store the received data
        received_data = data_payload.get("data", {})
        save_received_data(transfer_id, received_data)

        transfer["state"] = "COMPLETED"
        transfer["provider_state"] = "COMPLETED"
        transfer["completed_at"] = now
        transfer["has_data"] = True
        transfer["data_summary"] = {
            "received_at": now,
            "asset_id": data_payload.get("asset_id"),
            "data_keys": list(received_data.keys()) if isinstance(received_data, dict) else "array"
        }
        transfer["history"].append({
            "action": "COMPLETED",
            "timestamp": now,
            "data_received": True
        })

        save_transfer(transfer)
        log_event("DATA_RECEIVED", {
            "transfer_id": transfer_id,
            "asset_id": transfer.get("asset_id")
        })

        return {
            "status": "COMPLETED",
            "transfer_id": transfer_id,
            "asset_id": transfer.get("asset_id"),
            "message": "Data transfer completed successfully!",
            "data_endpoint": f"/api/transfers/{transfer_id}/data",
            "data_summary": transfer["data_summary"]
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PROVIDER_ERROR", "message": e.response.json()}
        )


@router.get("/{transfer_id}/data")
async def get_transfer_data(transfer_id: str):
    """Get the received data for a completed transfer."""
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    if transfer["state"] != "COMPLETED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "TRANSFER_NOT_COMPLETED",
                "message": f"Data only available for completed transfers. Current state: '{transfer['state']}'"
            }
        )

    data = get_received_data(transfer_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail={"error": "DATA_NOT_FOUND", "message": "No data stored for this transfer"}
        )

    return {
        "transfer_id": transfer_id,
        "asset_id": transfer.get("asset_id"),
        "received_at": transfer.get("completed_at"),
        "data": data
    }


@router.get("/received/all")
async def list_all_received_data():
    """List all received data from completed transfers."""
    received = get_all_received_data()

    return {
        "received_data": [
            {
                "transfer_id": transfer_id,
                "received_at": info["received_at"],
                "data_preview": str(info["data"])[:200] + "..." if len(str(info["data"])) > 200 else str(info["data"])
            }
            for transfer_id, info in received.items()
        ],
        "total": len(received)
    }


@router.get("/audit-log")
async def get_consumer_audit_log():
    """Get the consumer's audit log."""
    from store import get_audit_log

    log = get_audit_log()
    return {
        "audit_log": log,
        "total_events": len(log)
    }
