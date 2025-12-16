"""
Automotive EDC Provider Connector

This is a simulated Eclipse Dataspace Connector that demonstrates
the core concepts of sovereign data exchange for automotive OEMs.

The provider (OEM) offers datasets to consumers (suppliers) through
a catalog, handles contract negotiations, and manages data transfers.
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
from contracts import router as contracts_router
from transfers import router as transfers_router
from data_plane import router as data_plane_router
from store import initialize_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the in-memory store on startup."""
    initialize_store()
    yield


app = FastAPI(
    title="Automotive EDC Provider",
    description="""
    ## OEM Data Provider Connector

    This connector simulates an Eclipse Dataspace Connector (EDC) for an automotive OEM.
    It demonstrates sovereign data exchange following the Dataspace Protocol (DSP).

    ### Features:
    - **Catalog API**: Browse available datasets
    - **Contract Negotiation**: Request and negotiate data access
    - **Data Transfer**: Securely transfer data after agreement

    ### Automotive Data Available:
    - Part catalogs
    - Quality metrics
    - Battery traceability data
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
app.include_router(contracts_router, prefix="/api/negotiations", tags=["Contract Negotiation"])
app.include_router(transfers_router, prefix="/api/transfers", tags=["Data Transfer"])
app.include_router(data_plane_router, prefix="/api/data", tags=["Data Plane"])


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "connector": "provider",
        "name": "AutoMotors OEM Connector",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint with connector information."""
    return {
        "connector_id": "provider-automotors-oem",
        "connector_name": "AutoMotors OEM Data Provider",
        "connector_type": "provider",
        "description": "Eclipse Dataspace Connector simulation for automotive OEM",
        "endpoints": {
            "catalog": "/api/catalog",
            "negotiations": "/api/negotiations",
            "transfers": "/api/transfers",
            "health": "/health"
        },
        "dsp_version": "0.8"
    }


@app.get("/api/status")
async def get_status():
    """Get detailed connector status."""
    from store import get_store
    store = get_store()

    return {
        "connector_id": "provider-automotors-oem",
        "status": "operational",
        "statistics": {
            "assets": len(store.get("assets", [])),
            "active_negotiations": len([
                n for n in store.get("negotiations", {}).values()
                if n.get("state") not in ["FINALIZED", "TERMINATED"]
            ]),
            "completed_agreements": len(store.get("agreements", {})),
            "completed_transfers": len([
                t for t in store.get("transfers", {}).values()
                if t.get("state") == "COMPLETED"
            ])
        },
        "uptime": "operational",
        "last_updated": datetime.utcnow().isoformat()
    }


@app.post("/api/reset")
async def reset_demo():
    """Reset the demo state (clear all negotiations and transfers)."""
    initialize_store()
    return {
        "status": "reset",
        "message": "Demo state has been reset. Catalog preserved, negotiations and transfers cleared."
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
