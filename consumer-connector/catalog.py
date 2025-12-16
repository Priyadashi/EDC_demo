"""
Catalog API for Consumer Connector

Fetches and browses catalogs from provider connectors.
"""

import os
import httpx
from fastapi import APIRouter, HTTPException

from store import cache_catalog, get_cached_catalog, get_store

router = APIRouter()

# Provider endpoint - configurable via environment
PROVIDER_URL = os.getenv("PROVIDER_URL", "http://localhost:8080")


@router.get("/fetch")
async def fetch_provider_catalog():
    """
    Fetch the catalog from the provider connector.

    This simulates the DSP Catalog Request to get available datasets.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{PROVIDER_URL}/api/catalog")
            response.raise_for_status()
            catalog = response.json()

        # Cache the catalog
        provider_id = catalog.get("dspace:participantId", "unknown-provider")
        cache_catalog(provider_id, catalog)

        return {
            "status": "success",
            "provider": provider_id,
            "catalog": catalog,
            "cached": True
        }

    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "PROVIDER_UNREACHABLE",
                "message": f"Could not connect to provider at {PROVIDER_URL}",
                "hint": "Ensure the provider connector is running"
            }
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "error": "PROVIDER_ERROR",
                "message": f"Provider returned error: {e.response.text}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "FETCH_FAILED", "message": str(e)}
        )


@router.get("/cached")
async def get_cached_catalogs():
    """Get all cached catalogs."""
    store = get_store()
    cached = store.get("cached_catalogs", {})

    return {
        "cached_catalogs": [
            {
                "provider_id": provider_id,
                "cached_at": data["cached_at"],
                "dataset_count": len(data["catalog"].get("dspace:dataset", []))
            }
            for provider_id, data in cached.items()
        ]
    }


@router.get("/cached/{provider_id}")
async def get_provider_catalog(provider_id: str):
    """Get a cached catalog for a specific provider."""
    catalog = get_cached_catalog(provider_id)

    if not catalog:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "CATALOG_NOT_CACHED",
                "message": f"No cached catalog for provider '{provider_id}'",
                "hint": "Use GET /api/catalog/fetch to fetch the catalog first"
            }
        )

    return catalog


@router.get("/datasets")
async def list_available_datasets():
    """
    List all available datasets from cached catalogs.

    Provides a simplified view of all datasets the consumer can request.
    """
    store = get_store()
    cached = store.get("cached_catalogs", {})

    datasets = []
    for provider_id, data in cached.items():
        catalog = data["catalog"]
        for dataset in catalog.get("dspace:dataset", []):
            datasets.append({
                "provider_id": provider_id,
                "dataset_id": dataset.get("@id"),
                "title": dataset.get("dct:title"),
                "description": dataset.get("dct:description"),
                "format": dataset.get("dct:format"),
                "properties": dataset.get("properties", {}),
                "policy": dataset.get("odrl:hasPolicy", [{}])[0].get("policy", {}) if dataset.get("odrl:hasPolicy") else {}
            })

    return {
        "datasets": datasets,
        "total": len(datasets),
        "note": "Use POST /api/negotiations to request access to a dataset"
    }


@router.get("/datasets/{dataset_id}")
async def get_dataset_details(dataset_id: str):
    """Get details for a specific dataset."""
    store = get_store()
    cached = store.get("cached_catalogs", {})

    for provider_id, data in cached.items():
        catalog = data["catalog"]
        for dataset in catalog.get("dspace:dataset", []):
            if dataset.get("@id") == dataset_id:
                return {
                    "provider_id": provider_id,
                    "dataset": dataset,
                    "can_request": True,
                    "next_action": f"POST /api/negotiations with asset_id='{dataset_id}'"
                }

    raise HTTPException(
        status_code=404,
        detail={
            "error": "DATASET_NOT_FOUND",
            "message": f"Dataset '{dataset_id}' not found in cached catalogs",
            "hint": "Fetch the provider catalog first using GET /api/catalog/fetch"
        }
    )


@router.get("/preview/{dataset_id}")
async def preview_dataset(dataset_id: str):
    """
    Get a preview of a dataset from the provider.

    This fetches a limited preview without requiring a contract.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{PROVIDER_URL}/api/data/preview/{dataset_id}")
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={"error": "PREVIEW_FAILED", "message": e.response.text}
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "PREVIEW_FAILED", "message": str(e)}
        )
