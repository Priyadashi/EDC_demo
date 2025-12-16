"""
Catalog API for Provider Connector

Implements the Catalog Protocol from the Dataspace Protocol specification.
Allows consumers to browse available datasets and their access policies.
"""

import sys
import os
from fastapi import APIRouter, HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from shared.policies import POLICY_TEMPLATES, get_policy_description
from store import get_store, get_asset_by_id

router = APIRouter()


@router.get("")
@router.get("/")
async def get_catalog():
    """
    Get the complete catalog of available datasets.

    Returns a DSP-compliant catalog with all datasets and their offers.
    Each dataset includes metadata, properties, and access policies.
    """
    store = get_store()
    assets = store.get("assets", [])

    datasets = []
    for asset in assets:
        policy = POLICY_TEMPLATES.get(asset.get("policy_id", "open-access"))

        dataset = {
            "@id": asset["id"],
            "@type": "dspace:Dataset",
            "dct:title": asset["name"],
            "dct:description": asset["description"],
            "dct:format": asset["content_type"],
            "properties": asset.get("properties", {}),
            "odrl:hasPolicy": [
                {
                    "@id": f"offer-{asset['id']}",
                    "@type": "odrl:Offer",
                    "policy": {
                        "id": policy.id,
                        "description": get_policy_description(policy),
                        "permissions": [
                            {
                                "action": p.action,
                                "constraints": [
                                    {
                                        "leftOperand": c.left_operand,
                                        "operator": c.operator,
                                        "rightOperand": c.right_operand
                                    }
                                    for c in p.constraints
                                ]
                            }
                            for p in policy.permissions
                        ],
                        "prohibitions": [
                            {"action": p.action}
                            for p in policy.prohibitions
                        ]
                    }
                }
            ]
        }
        datasets.append(dataset)

    return {
        "@context": {
            "@vocab": "https://w3id.org/dspace/",
            "dct": "http://purl.org/dc/terms/",
            "odrl": "http://www.w3.org/ns/odrl/2/"
        },
        "@type": "dspace:Catalog",
        "dspace:participantId": "provider-automotors-oem",
        "dspace:dataset": datasets
    }


@router.get("/datasets")
async def list_datasets():
    """
    Get a simplified list of available datasets.

    Returns a list of datasets with basic info for easy consumption.
    """
    store = get_store()
    assets = store.get("assets", [])

    return {
        "datasets": [
            {
                "id": asset["id"],
                "name": asset["name"],
                "description": asset["description"],
                "content_type": asset["content_type"],
                "properties": asset.get("properties", {}),
                "policy_id": asset.get("policy_id", "open-access")
            }
            for asset in assets
        ],
        "total": len(assets)
    }


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """
    Get details for a specific dataset.

    Args:
        dataset_id: The unique identifier of the dataset

    Returns:
        Dataset details including metadata and access policy
    """
    asset = get_asset_by_id(dataset_id)

    if not asset:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "DATASET_NOT_FOUND",
                "message": f"Dataset '{dataset_id}' not found in catalog",
                "hint": "Use GET /api/catalog/datasets to see available datasets"
            }
        )

    policy = POLICY_TEMPLATES.get(asset.get("policy_id", "open-access"))

    return {
        "@context": {
            "@vocab": "https://w3id.org/dspace/",
            "dct": "http://purl.org/dc/terms/",
            "odrl": "http://www.w3.org/ns/odrl/2/"
        },
        "@type": "dspace:Dataset",
        "@id": asset["id"],
        "dct:title": asset["name"],
        "dct:description": asset["description"],
        "dct:format": asset["content_type"],
        "properties": asset.get("properties", {}),
        "odrl:hasPolicy": {
            "@id": f"offer-{asset['id']}",
            "@type": "odrl:Offer",
            "policy": {
                "id": policy.id,
                "description": get_policy_description(policy),
                "permissions": [
                    {
                        "action": p.action,
                        "constraints": [
                            {
                                "leftOperand": c.left_operand,
                                "operator": c.operator,
                                "rightOperand": c.right_operand
                            }
                            for c in p.constraints
                        ]
                    }
                    for p in policy.permissions
                ],
                "prohibitions": [
                    {"action": p.action}
                    for p in policy.prohibitions
                ]
            }
        }
    }


@router.get("/policies")
async def list_policies():
    """
    List all available policy templates.

    Returns descriptions of policies that can be applied to datasets.
    """
    return {
        "policies": [
            {
                "id": policy_id,
                "description": get_policy_description(policy),
                "permissions": len(policy.permissions),
                "prohibitions": len(policy.prohibitions)
            }
            for policy_id, policy in POLICY_TEMPLATES.items()
        ]
    }


@router.get("/policies/{policy_id}")
async def get_policy(policy_id: str):
    """
    Get details for a specific policy.

    Args:
        policy_id: The policy identifier

    Returns:
        Full policy details including all rules
    """
    policy = POLICY_TEMPLATES.get(policy_id)

    if not policy:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "POLICY_NOT_FOUND",
                "message": f"Policy '{policy_id}' not found",
                "hint": "Use GET /api/catalog/policies to see available policies"
            }
        )

    return {
        "id": policy.id,
        "description": get_policy_description(policy),
        "permissions": [
            {
                "action": p.action,
                "constraints": [
                    {
                        "leftOperand": c.left_operand,
                        "operator": c.operator,
                        "rightOperand": c.right_operand,
                        "description": f"Requires {c.left_operand} to be {c.operator} {c.right_operand}"
                    }
                    for c in p.constraints
                ]
            }
            for p in policy.permissions
        ],
        "prohibitions": [
            {
                "action": p.action,
                "description": f"The action '{p.action}' is not allowed"
            }
            for p in policy.prohibitions
        ]
    }
