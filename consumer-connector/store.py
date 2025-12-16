"""
In-Memory Store for Consumer Connector

Stores cached catalogs, negotiations, agreements, and received data.
"""

import os
from datetime import datetime
from typing import Any

# Global in-memory store
_store: dict = {}


def get_store() -> dict:
    """Get the in-memory store."""
    global _store
    return _store


def initialize_store():
    """Initialize the store with consumer identity."""
    global _store

    _store = {
        "identity": {
            "consumer_id": "consumer-tierone-supplier",
            "company_name": "TierOne Electronics GmbH",
            "partner_type": "tier1_supplier",
            "region": "EU",
            "certifications": ["TISAX", "ISO27001", "IATF16949"],
            "purpose": "quality_analysis"
        },
        "cached_catalogs": {},
        "negotiations": {},
        "agreements": {},
        "transfers": {},
        "received_data": {},
        "audit_log": []
    }

    _store["audit_log"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": "STORE_INITIALIZED",
        "details": "Consumer connector initialized"
    })


def log_event(event_type: str, details: Any):
    """Log an audit event."""
    global _store
    _store["audit_log"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "event": event_type,
        "details": details
    })


def get_identity() -> dict:
    """Get consumer identity attributes."""
    global _store
    return _store.get("identity", {})


def cache_catalog(provider_id: str, catalog: dict):
    """Cache a provider's catalog."""
    global _store
    _store["cached_catalogs"][provider_id] = {
        "catalog": catalog,
        "cached_at": datetime.utcnow().isoformat()
    }
    log_event("CATALOG_CACHED", {"provider_id": provider_id})


def get_cached_catalog(provider_id: str) -> dict | None:
    """Get a cached catalog."""
    global _store
    cached = _store["cached_catalogs"].get(provider_id)
    return cached["catalog"] if cached else None


def save_negotiation(negotiation: dict):
    """Save a negotiation."""
    global _store
    _store["negotiations"][negotiation["id"]] = negotiation
    log_event("NEGOTIATION_SAVED", {"negotiation_id": negotiation["id"]})


def get_negotiation(negotiation_id: str) -> dict | None:
    """Get a negotiation by ID."""
    global _store
    return _store["negotiations"].get(negotiation_id)


def get_all_negotiations() -> list:
    """Get all negotiations."""
    global _store
    return list(_store["negotiations"].values())


def save_agreement(agreement: dict):
    """Save an agreement."""
    global _store
    _store["agreements"][agreement["id"]] = agreement
    log_event("AGREEMENT_SAVED", {"agreement_id": agreement["id"]})


def get_agreement(agreement_id: str) -> dict | None:
    """Get an agreement by ID."""
    global _store
    return _store["agreements"].get(agreement_id)


def get_all_agreements() -> list:
    """Get all agreements."""
    global _store
    return list(_store["agreements"].values())


def save_transfer(transfer: dict):
    """Save a transfer."""
    global _store
    _store["transfers"][transfer["id"]] = transfer
    log_event("TRANSFER_SAVED", {"transfer_id": transfer["id"]})


def get_transfer(transfer_id: str) -> dict | None:
    """Get a transfer by ID."""
    global _store
    return _store["transfers"].get(transfer_id)


def get_all_transfers() -> list:
    """Get all transfers."""
    global _store
    return list(_store["transfers"].values())


def save_received_data(transfer_id: str, data: dict):
    """Save received data from a transfer."""
    global _store
    _store["received_data"][transfer_id] = {
        "data": data,
        "received_at": datetime.utcnow().isoformat()
    }
    log_event("DATA_RECEIVED", {"transfer_id": transfer_id})


def get_received_data(transfer_id: str) -> dict | None:
    """Get received data by transfer ID."""
    global _store
    received = _store["received_data"].get(transfer_id)
    return received["data"] if received else None


def get_all_received_data() -> dict:
    """Get all received data."""
    global _store
    return _store.get("received_data", {})


def get_audit_log() -> list:
    """Get the audit log."""
    global _store
    return _store.get("audit_log", [])
