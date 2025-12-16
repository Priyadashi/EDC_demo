"""
Data Plane API for Provider Connector

The Data Plane handles the actual data serving.
In a real EDC, this would be a separate component that
handles the physical data transfer using various protocols.
"""

import sys
import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from store import get_asset_data, get_asset_by_id, get_transfer, get_agreement

router = APIRouter()


@router.get("/preview/{asset_id}")
async def preview_asset(asset_id: str):
    """
    Get a preview of an asset's data.

    This provides a limited preview without requiring a contract.
    Useful for understanding what data is available.
    """
    asset = get_asset_by_id(asset_id)

    if not asset:
        raise HTTPException(
            status_code=404,
            detail={"error": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' not found"}
        )

    data = get_asset_data(asset_id)

    if not data:
        return {
            "asset_id": asset_id,
            "name": asset["name"],
            "preview": "Preview not available",
            "message": "Initiate a contract negotiation to access full data"
        }

    # Create a limited preview (first level of structure only)
    preview = {}
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "metadata":
                preview[key] = value
            elif isinstance(value, dict):
                preview[key] = f"<object with {len(value)} keys>"
            elif isinstance(value, list):
                preview[key] = f"<array with {len(value)} items>"
            else:
                preview[key] = value

    return {
        "asset_id": asset_id,
        "name": asset["name"],
        "description": asset["description"],
        "content_type": asset["content_type"],
        "preview": preview,
        "note": "This is a limited preview. Complete a contract negotiation to access full data."
    }


@router.get("/agreements")
async def list_agreements():
    """List all active agreements."""
    from store import get_all_agreements

    agreements = get_all_agreements()

    return {
        "agreements": [
            {
                "id": a["id"],
                "asset_id": a["asset_id"],
                "consumer_id": a["consumer_id"],
                "signing_date": a["signing_date"],
                "status": a.get("status", "ACTIVE")
            }
            for a in agreements
        ],
        "total": len(agreements)
    }


@router.get("/audit-log")
async def get_audit_log():
    """Get the audit log of all operations."""
    from store import get_audit_log

    log = get_audit_log()

    return {
        "audit_log": log,
        "total_events": len(log)
    }
