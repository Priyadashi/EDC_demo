"""
Dataspace Protocol (DSP) Implementation

This module implements the core message types and protocol logic for the
Dataspace Protocol, which enables sovereign data exchange between connectors.

Reference: https://docs.internationaldataspaces.org/ids-knowledgebase/dataspace-protocol
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
import uuid


class DSPMessage(BaseModel):
    """Base class for all DSP messages."""
    context: dict = Field(
        default={
            "@vocab": "https://w3id.org/dspace/",
            "dct": "http://purl.org/dc/terms/",
            "odrl": "http://www.w3.org/ns/odrl/2/"
        },
        alias="@context"
    )
    type: str = Field(..., alias="@type")

    class Config:
        populate_by_name = True


# Catalog Protocol Messages

class CatalogRequestMessage(DSPMessage):
    """Request to retrieve a catalog from a provider."""
    type: str = Field(default="dspace:CatalogRequestMessage", alias="@type")
    filter: Optional[dict] = None


class CatalogMessage(DSPMessage):
    """Response containing the catalog."""
    type: str = Field(default="dspace:Catalog", alias="@type")
    participant_id: str = Field(..., alias="dspace:participantId")
    datasets: list[dict] = Field(default=[], alias="dspace:dataset")


class DatasetMessage(DSPMessage):
    """A single dataset in the catalog."""
    type: str = Field(default="dspace:Dataset", alias="@type")
    id: str = Field(..., alias="@id")
    title: str = Field(..., alias="dct:title")
    description: str = Field(..., alias="dct:description")
    offers: list[dict] = Field(default=[], alias="odrl:hasPolicy")


# Contract Negotiation Protocol Messages

class ContractRequestMessage(DSPMessage):
    """Initial request from consumer to start negotiation."""
    type: str = Field(default="dspace:ContractRequestMessage", alias="@type")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    offer: dict = Field(..., alias="dspace:offer")
    callback_address: str = Field(..., alias="dspace:callbackAddress")


class ContractOfferMessage(DSPMessage):
    """Offer from provider to consumer."""
    type: str = Field(default="dspace:ContractOfferMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    offer: dict = Field(..., alias="dspace:offer")
    callback_address: str = Field(..., alias="dspace:callbackAddress")


class ContractAgreementMessage(DSPMessage):
    """Agreement message after both parties agree."""
    type: str = Field(default="dspace:ContractAgreementMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    agreement: dict = Field(..., alias="dspace:agreement")
    callback_address: str = Field(..., alias="dspace:callbackAddress")


class ContractAgreementVerificationMessage(DSPMessage):
    """Verification of the agreement."""
    type: str = Field(default="dspace:ContractAgreementVerificationMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")


class ContractNegotiationEventMessage(DSPMessage):
    """Event message for negotiation state changes."""
    type: str = Field(default="dspace:ContractNegotiationEventMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    event_type: str = Field(..., alias="dspace:eventType")


class ContractNegotiationTerminationMessage(DSPMessage):
    """Message to terminate a negotiation."""
    type: str = Field(default="dspace:ContractNegotiationTerminationMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    code: Optional[str] = None
    reason: list[dict] = []


# Transfer Process Protocol Messages

class TransferRequestMessage(DSPMessage):
    """Request to initiate a data transfer."""
    type: str = Field(default="dspace:TransferRequestMessage", alias="@type")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    agreement_id: str = Field(..., alias="dspace:agreementId")
    format: str = Field(default="HTTP_PUSH", alias="dct:format")
    data_address: Optional[dict] = Field(None, alias="dspace:dataAddress")
    callback_address: str = Field(..., alias="dspace:callbackAddress")


class TransferStartMessage(DSPMessage):
    """Message indicating transfer has started."""
    type: str = Field(default="dspace:TransferStartMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    data_address: Optional[dict] = Field(None, alias="dspace:dataAddress")


class TransferCompletionMessage(DSPMessage):
    """Message indicating transfer is complete."""
    type: str = Field(default="dspace:TransferCompletionMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")


class TransferTerminationMessage(DSPMessage):
    """Message to terminate a transfer."""
    type: str = Field(default="dspace:TransferTerminationMessage", alias="@type")
    provider_pid: str = Field(..., alias="dspace:providerPid")
    consumer_pid: str = Field(..., alias="dspace:consumerPid")
    code: Optional[str] = None
    reason: list[dict] = []


# Error Messages

class DSPErrorMessage(DSPMessage):
    """Error response message."""
    type: str = Field(default="dspace:ContractNegotiationError", alias="@type")
    provider_pid: Optional[str] = Field(None, alias="dspace:providerPid")
    consumer_pid: Optional[str] = Field(None, alias="dspace:consumerPid")
    code: str
    reason: list[dict] = []


# Helper functions for creating DSP-compliant messages

def create_catalog_response(
    participant_id: str,
    datasets: list[dict]
) -> dict:
    """Create a DSP-compliant catalog response."""
    return {
        "@context": {
            "@vocab": "https://w3id.org/dspace/",
            "dct": "http://purl.org/dc/terms/",
            "odrl": "http://www.w3.org/ns/odrl/2/"
        },
        "@type": "dspace:Catalog",
        "dspace:participantId": participant_id,
        "dspace:dataset": datasets
    }


def create_negotiation_response(
    negotiation_id: str,
    state: str,
    provider_pid: str,
    consumer_pid: str
) -> dict:
    """Create a DSP-compliant negotiation status response."""
    return {
        "@context": {
            "@vocab": "https://w3id.org/dspace/"
        },
        "@type": "dspace:ContractNegotiation",
        "@id": negotiation_id,
        "dspace:state": state,
        "dspace:providerPid": provider_pid,
        "dspace:consumerPid": consumer_pid
    }


def create_transfer_response(
    transfer_id: str,
    state: str,
    provider_pid: str,
    consumer_pid: str
) -> dict:
    """Create a DSP-compliant transfer process response."""
    return {
        "@context": {
            "@vocab": "https://w3id.org/dspace/"
        },
        "@type": "dspace:TransferProcess",
        "@id": transfer_id,
        "dspace:state": state,
        "dspace:providerPid": provider_pid,
        "dspace:consumerPid": consumer_pid
    }


def create_error_response(
    code: str,
    reason: str,
    provider_pid: Optional[str] = None,
    consumer_pid: Optional[str] = None
) -> dict:
    """Create a DSP-compliant error response."""
    return {
        "@context": {
            "@vocab": "https://w3id.org/dspace/"
        },
        "@type": "dspace:Error",
        "dspace:code": code,
        "dspace:reason": [{"@value": reason, "@language": "en"}],
        "dspace:providerPid": provider_pid,
        "dspace:consumerPid": consumer_pid
    }
