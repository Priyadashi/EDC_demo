"""
Automotive EDC Consumer Connector

This is a simulated Eclipse Dataspace Connector for a Tier-1 Supplier.
The consumer fetches catalogs from providers, initiates contract negotiations,
and receives data transfers.
"""

import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from catalog import router as catalog_router
from negotiations import router as negotiations_router
from transfers import router as transfers_router
from store import initialize_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the in-memory store on startup."""
    initialize_store()
    yield


app = FastAPI(
    title="Automotive EDC Consumer",
    description="""
    ## Tier-1 Supplier Consumer Connector

    This connector simulates an Eclipse Dataspace Connector (EDC) for a Tier-1 automotive supplier.
    It demonstrates how to consume data from an OEM provider using the Dataspace Protocol.

    ### Features:
    - **Catalog Browsing**: Fetch and browse provider catalogs
    - **Contract Negotiation**: Request access to datasets
    - **Data Reception**: Receive and store transferred data

    ### Consumer Identity:
    - Company: TierOne Electronics GmbH
    - Partner Type: tier1_supplier
    - Certifications: TISAX, ISO27001, IATF16949
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for demo UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(catalog_router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(negotiations_router, prefix="/api/negotiations", tags=["Contract Negotiation"])
app.include_router(transfers_router, prefix="/api/transfers", tags=["Data Transfer"])


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "connector": "consumer",
        "name": "TierOne Electronics Connector",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with connector information."""
    return {
        "connector_id": "consumer-tierone-supplier",
        "connector_name": "TierOne Electronics GmbH Consumer",
        "connector_type": "consumer",
        "description": "Eclipse Dataspace Connector simulation for Tier-1 Supplier",
        "identity": {
            "company_name": "TierOne Electronics GmbH",
            "partner_type": "tier1_supplier",
            "region": "EU",
            "certifications": ["TISAX", "ISO27001", "IATF16949"]
        },
        "endpoints": {
            "catalog": "/api/catalog",
            "negotiations": "/api/negotiations",
            "transfers": "/api/transfers",
            "health": "/health"
        },
        "dsp_version": "0.8"
    }


@app.get("/api/identity")
async def get_identity():
    """Get the consumer's identity attributes used for policy evaluation."""
    from store import get_store
    store = get_store()

    return store.get("identity", {
        "consumer_id": "consumer-tierone-supplier",
        "company_name": "TierOne Electronics GmbH",
        "partner_type": "tier1_supplier",
        "region": "EU",
        "certifications": ["TISAX", "ISO27001", "IATF16949"],
        "purpose": "quality_analysis"
    })


@app.put("/api/identity")
async def update_identity(identity: dict):
    """Update the consumer's identity attributes (for demo purposes)."""
    from store import get_store, log_event
    store = get_store()

    # Preserve consumer_id
    identity["consumer_id"] = "consumer-tierone-supplier"
    store["identity"] = identity

    log_event("IDENTITY_UPDATED", identity)

    return {
        "status": "updated",
        "identity": identity,
        "note": "Identity updated. This affects policy evaluation during negotiations."
    }


@app.get("/api/status")
async def get_status():
    """Get detailed connector status."""
    from store import get_store
    store = get_store()

    return {
        "connector_id": "consumer-tierone-supplier",
        "status": "operational",
        "statistics": {
            "cached_catalogs": len(store.get("cached_catalogs", {})),
            "active_negotiations": len([
                n for n in store.get("negotiations", {}).values()
                if n.get("state") not in ["FINALIZED", "TERMINATED"]
            ]),
            "agreements": len(store.get("agreements", {})),
            "received_data": len(store.get("received_data", {}))
        },
        "identity": store.get("identity", {}),
        "last_updated": datetime.utcnow().isoformat()
    }


@app.post("/api/reset")
async def reset_demo():
    """Reset the demo state."""
    initialize_store()
    return {
        "status": "reset",
        "message": "Consumer state has been reset."
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8081))
    uvicorn.run(app, host="0.0.0.0", port=port)
