"""
Transfer Process API for Provider Connector

Implements the Transfer Process Protocol from the Dataspace Protocol.
Handles data transfer initiation, execution, and completion.
"""

import sys
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from store import (
    get_agreement, get_transfer, save_transfer,
    get_asset_data, get_asset_by_id, log_event, get_all_transfers
)

router = APIRouter()


class TransferRequest(BaseModel):
    """Request to initiate a data transfer."""
    agreement_id: str
    data_destination: Optional[str] = None
    format: Optional[str] = "HTTP_PUSH"


@router.get("")
@router.get("/")
async def list_transfers():
    """List all transfer processes."""
    transfers = get_all_transfers()

    return {
        "transfers": [
            {
                "id": t["id"],
                "state": t["state"],
                "agreement_id": t["agreement_id"],
                "asset_id": t["asset_id"],
                "created_at": t["created_at"],
                "completed_at": t.get("completed_at")
            }
            for t in transfers
        ],
        "total": len(transfers)
    }


@router.post("")
@router.post("/")
async def initiate_transfer(request: TransferRequest):
    """
    Initiate a data transfer.

    Requires a valid agreement_id from a finalized contract negotiation.
    """
    # Verify agreement exists
    agreement = get_agreement(request.agreement_id)

    if not agreement:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "AGREEMENT_NOT_FOUND",
                "message": f"Agreement '{request.agreement_id}' not found",
                "hint": "Complete a contract negotiation first to obtain an agreement_id"
            }
        )

    if agreement.get("status") != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "AGREEMENT_NOT_ACTIVE",
                "message": "Agreement is not active"
            }
        )

    # Create transfer process
    transfer_id = f"transfer-{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat()

    transfer = {
        "id": transfer_id,
        "state": "REQUESTED",
        "agreement_id": request.agreement_id,
        "asset_id": agreement["asset_id"],
        "provider_id": agreement["provider_id"],
        "consumer_id": agreement["consumer_id"],
        "data_destination": request.data_destination,
        "format": request.format,
        "created_at": now,
        "state_history": [
            {"state": "REQUESTED", "timestamp": now}
        ]
    }

    save_transfer(transfer)
    log_event("TRANSFER_INITIATED", {
        "transfer_id": transfer_id,
        "agreement_id": request.agreement_id
    })

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:TransferProcess",
        "@id": transfer_id,
        "dspace:state": "REQUESTED",
        "dspace:agreementId": request.agreement_id,
        "asset_id": agreement["asset_id"],
        "message": "Transfer process initiated. Ready to start data transfer.",
        "next_action": "POST /api/transfers/{id}/start to begin data transfer"
    }


@router.get("/{transfer_id}")
async def get_transfer_status(transfer_id: str):
    """Get the current status of a transfer."""
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(
            status_code=404,
            detail={"error": "TRANSFER_NOT_FOUND", "message": f"Transfer '{transfer_id}' not found"}
        )

    asset = get_asset_by_id(transfer["asset_id"])

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:TransferProcess",
        "@id": transfer["id"],
        "dspace:state": transfer["state"],
        "dspace:agreementId": transfer["agreement_id"],
        "dspace:providerPid": transfer["provider_id"],
        "dspace:consumerPid": transfer["consumer_id"],
        "asset": {
            "id": asset["id"] if asset else transfer["asset_id"],
            "name": asset["name"] if asset else "Unknown"
        },
        "state_history": transfer.get("state_history", []),
        "created_at": transfer["created_at"],
        "completed_at": transfer.get("completed_at"),
        "has_data": transfer.get("data") is not None
    }


@router.post("/{transfer_id}/start")
async def start_transfer(transfer_id: str):
    """
    Start the data transfer.

    This begins the actual data movement from provider to consumer.
    """
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    if transfer["state"] != "REQUESTED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Cannot start in state '{transfer['state']}'. Expected 'REQUESTED'."
            }
        )

    now = datetime.utcnow().isoformat()
    transfer["state"] = "STARTED"
    transfer["started_at"] = now
    transfer["state_history"].append({
        "state": "STARTED",
        "timestamp": now
    })

    save_transfer(transfer)
    log_event("TRANSFER_STARTED", {"transfer_id": transfer_id})

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:TransferStartMessage",
        "dspace:providerPid": transfer["provider_id"],
        "dspace:consumerPid": transfer["consumer_id"],
        "dspace:state": "STARTED",
        "message": "Data transfer in progress.",
        "next_action": "POST /api/transfers/{id}/complete to finalize transfer"
    }


@router.post("/{transfer_id}/complete")
async def complete_transfer(transfer_id: str):
    """
    Complete the data transfer and deliver data to consumer.

    This loads the actual data and makes it available.
    """
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    if transfer["state"] != "STARTED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Cannot complete in state '{transfer['state']}'. Expected 'STARTED'."
            }
        )

    # Load the actual data
    data = get_asset_data(transfer["asset_id"])

    if not data:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "DATA_NOT_AVAILABLE",
                "message": "Could not load asset data"
            }
        )

    now = datetime.utcnow().isoformat()
    transfer["state"] = "COMPLETED"
    transfer["completed_at"] = now
    transfer["data"] = data
    transfer["state_history"].append({
        "state": "COMPLETED",
        "timestamp": now,
        "data_size": len(str(data))
    })

    save_transfer(transfer)
    log_event("TRANSFER_COMPLETED", {
        "transfer_id": transfer_id,
        "asset_id": transfer["asset_id"]
    })

    asset = get_asset_by_id(transfer["asset_id"])

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:TransferCompletionMessage",
        "dspace:providerPid": transfer["provider_id"],
        "dspace:consumerPid": transfer["consumer_id"],
        "dspace:state": "COMPLETED",
        "asset": {
            "id": asset["id"] if asset else transfer["asset_id"],
            "name": asset["name"] if asset else "Unknown"
        },
        "message": "Data transfer completed successfully!",
        "data_endpoint": f"/api/transfers/{transfer_id}/data",
        "hint": "Use GET /api/transfers/{id}/data to retrieve the transferred data"
    }


@router.get("/{transfer_id}/data")
async def get_transferred_data(transfer_id: str):
    """
    Get the transferred data.

    Only available for completed transfers.
    """
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

    data = transfer.get("data")
    if not data:
        data = get_asset_data(transfer["asset_id"])

    if not data:
        raise HTTPException(
            status_code=500,
            detail={"error": "DATA_NOT_AVAILABLE", "message": "Could not retrieve data"}
        )

    return {
        "transfer_id": transfer_id,
        "asset_id": transfer["asset_id"],
        "consumer_id": transfer["consumer_id"],
        "transferred_at": transfer["completed_at"],
        "data": data
    }


@router.post("/{transfer_id}/suspend")
async def suspend_transfer(transfer_id: str):
    """Suspend an in-progress transfer."""
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    if transfer["state"] != "STARTED":
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Cannot suspend in state '{transfer['state']}'"
            }
        )

    now = datetime.utcnow().isoformat()
    transfer["state"] = "SUSPENDED"
    transfer["state_history"].append({
        "state": "SUSPENDED",
        "timestamp": now
    })

    save_transfer(transfer)
    log_event("TRANSFER_SUSPENDED", {"transfer_id": transfer_id})

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:TransferProcess",
        "dspace:state": "SUSPENDED",
        "message": "Transfer suspended."
    }


@router.post("/{transfer_id}/terminate")
async def terminate_transfer(transfer_id: str):
    """Terminate a transfer."""
    transfer = get_transfer(transfer_id)

    if not transfer:
        raise HTTPException(status_code=404, detail={"error": "TRANSFER_NOT_FOUND"})

    if transfer["state"] in ["COMPLETED", "TERMINATED"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_STATE",
                "message": f"Transfer already in final state '{transfer['state']}'"
            }
        )

    now = datetime.utcnow().isoformat()
    transfer["state"] = "TERMINATED"
    transfer["state_history"].append({
        "state": "TERMINATED",
        "timestamp": now
    })

    save_transfer(transfer)
    log_event("TRANSFER_TERMINATED", {"transfer_id": transfer_id})

    return {
        "@context": {"@vocab": "https://w3id.org/dspace/"},
        "@type": "dspace:TransferTerminationMessage",
        "dspace:state": "TERMINATED",
        "message": "Transfer terminated."
    }
