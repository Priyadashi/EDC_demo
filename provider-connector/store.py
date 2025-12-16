"""
In-Memory Store for Provider Connector

This module provides a simple in-memory store for the demo.
In a production EDC, this would be backed by a database.

Note: Cloud Run containers are stateless, so this state resets
when the container restarts. This is acceptable for demo purposes.
"""

import json
import os
from typing import Any
from datetime import datetime

# Global in-memory store
_store: dict = {}


def get_store() -> dict:
    """Get the in-memory store."""
    global _store
    return _store


def initialize_store():
    """Initialize the store with sample automotive data."""
    global _store

    # Load sample data
    sample_data_dir = os.path.join(os.path.dirname(__file__), '..', 'sample-data')

    # Define assets based on sample data
    _store = {
        "assets": [
            {
                "id": "part-catalog-2024",
                "name": "2024 Vehicle Part Catalog",
                "description": "Complete parts catalog for 2024 model year electric vehicles including powertrain, battery, and chassis components.",
                "content_type": "application/json",
                "properties": {
                    "automotive:dataCategory": "parts-master",
                    "automotive:vehicleModels": ["EV-Sport", "EV-Sedan", "EV-SUV"],
                    "automotive:partCount": 15420,
                    "automotive:lastUpdated": "2024-12-01",
                    "automotive:confidentiality": "internal"
                },
                "policy_id": "tier1-only",
                "data_file": "part-catalog.json"
            },
            {
                "id": "quality-metrics-q4",
                "name": "Q4 2024 Quality Metrics",
                "description": "Supplier quality performance data for Q4 2024, including PPM rates, delivery performance, and corrective actions.",
                "content_type": "application/json",
                "properties": {
                    "automotive:dataCategory": "quality",
                    "automotive:reportingPeriod": "2024-Q4",
                    "automotive:confidentiality": "restricted",
                    "automotive:suppliers": ["TierOne Electronics", "BatteryCell Corp", "DriveSystem Parts", "SuspensionTech"]
                },
                "policy_id": "quality-data",
                "data_file": "quality-data.json"
            },
            {
                "id": "traceability-batch-001",
                "name": "Battery Traceability Data",
                "description": "Complete traceability data for battery components including raw material origins, manufacturing data, and carbon footprint.",
                "content_type": "application/json",
                "properties": {
                    "automotive:dataCategory": "traceability",
                    "automotive:componentType": "battery",
                    "automotive:regulatoryCompliance": ["EU-Battery-Regulation-2023", "UN38.3"],
                    "automotive:carbonFootprint": true
                },
                "policy_id": "certified-partners",
                "data_file": "traceability-data.json"
            }
        ],
        "negotiations": {},
        "agreements": {},
        "transfers": {},
        "audit_log": []
    }

    # Log initialization
    _store["audit_log"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "STORE_INITIALIZED",
        "details": f"Initialized with {len(_store['assets'])} assets"
    })


def log_event(event_type: str, details: dict):
    """Log an audit event."""
    global _store
    _store["audit_log"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "details": details
    })


def get_asset_by_id(asset_id: str) -> dict | None:
    """Get an asset by its ID."""
    global _store
    for asset in _store.get("assets", []):
        if asset["id"] == asset_id:
            return asset
    return None


def get_asset_data(asset_id: str) -> dict | None:
    """Load the actual data for an asset from the sample data files."""
    asset = get_asset_by_id(asset_id)
    if not asset:
        return None

    data_file = asset.get("data_file")
    if not data_file:
        return None

    sample_data_path = os.path.join(
        os.path.dirname(__file__), '..', 'sample-data', data_file
    )

    try:
        with open(sample_data_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def save_negotiation(negotiation: dict):
    """Save a negotiation to the store."""
    global _store
    _store["negotiations"][negotiation["id"]] = negotiation
    log_event("NEGOTIATION_SAVED", {"negotiation_id": negotiation["id"], "state": negotiation["state"]})


def get_negotiation(negotiation_id: str) -> dict | None:
    """Get a negotiation by ID."""
    global _store
    return _store["negotiations"].get(negotiation_id)


def save_agreement(agreement: dict):
    """Save an agreement to the store."""
    global _store
    _store["agreements"][agreement["id"]] = agreement
    log_event("AGREEMENT_SAVED", {"agreement_id": agreement["id"]})


def get_agreement(agreement_id: str) -> dict | None:
    """Get an agreement by ID."""
    global _store
    return _store["agreements"].get(agreement_id)


def save_transfer(transfer: dict):
    """Save a transfer to the store."""
    global _store
    _store["transfers"][transfer["id"]] = transfer
    log_event("TRANSFER_SAVED", {"transfer_id": transfer["id"], "state": transfer["state"]})


def get_transfer(transfer_id: str) -> dict | None:
    """Get a transfer by ID."""
    global _store
    return _store["transfers"].get(transfer_id)


def get_all_negotiations() -> list:
    """Get all negotiations."""
    global _store
    return list(_store["negotiations"].values())


def get_all_agreements() -> list:
    """Get all agreements."""
    global _store
    return list(_store["agreements"].values())


def get_all_transfers() -> list:
    """Get all transfers."""
    global _store
    return list(_store["transfers"].values())


def get_audit_log() -> list:
    """Get the audit log."""
    global _store
    return _store.get("audit_log", [])
