"""
EDC Data Models - Pydantic models for Eclipse Dataspace Connector concepts.

These models represent the core data structures used in the Dataspace Protocol (DSP)
for sovereign data exchange between automotive partners.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel, Field
import uuid


class NegotiationState(str, Enum):
    """States for contract negotiation state machine."""
    REQUESTED = "REQUESTED"
    OFFERED = "OFFERED"
    AGREED = "AGREED"
    VERIFIED = "VERIFIED"
    FINALIZED = "FINALIZED"
    TERMINATED = "TERMINATED"


class TransferState(str, Enum):
    """States for data transfer process."""
    REQUESTED = "REQUESTED"
    STARTED = "STARTED"
    SUSPENDED = "SUSPENDED"
    COMPLETED = "COMPLETED"
    TERMINATED = "TERMINATED"


class Constraint(BaseModel):
    """Policy constraint for access control."""
    left_operand: str = Field(..., alias="leftOperand")
    operator: str  # eq, neq, in, gt, lt, etc.
    right_operand: Any = Field(..., alias="rightOperand")

    class Config:
        populate_by_name = True


class Permission(BaseModel):
    """Permission granted by a policy."""
    action: str  # USE, DISTRIBUTE, MODIFY, etc.
    constraints: list[Constraint] = []


class Prohibition(BaseModel):
    """Prohibition defined by a policy."""
    action: str
    constraints: list[Constraint] = []


class Obligation(BaseModel):
    """Obligation required by a policy."""
    action: str
    constraints: list[Constraint] = []


class Policy(BaseModel):
    """
    ODRL-based policy for data access control.

    Policies define who can access data and under what conditions.
    In automotive context, this might restrict access to certified partners,
    limit usage to specific purposes, or require data deletion after use.
    """
    id: str = Field(default_factory=lambda: f"policy-{uuid.uuid4().hex[:8]}")
    permissions: list[Permission] = []
    prohibitions: list[Prohibition] = []
    obligations: list[Obligation] = []


class Asset(BaseModel):
    """
    Represents a data asset offered by a provider.

    In automotive context, this could be:
    - Part catalogs
    - Quality metrics
    - Traceability data
    - Production schedules
    """
    id: str
    name: str
    description: str
    content_type: str = "application/json"
    properties: dict = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DatasetEntry(BaseModel):
    """A dataset entry in the catalog (combines asset with offer info)."""
    id: str
    asset: Asset
    offers: list["ContractOffer"] = []


class ContractOffer(BaseModel):
    """
    Offer from provider to consumer.

    Represents the terms under which a dataset can be accessed.
    """
    id: str = Field(default_factory=lambda: f"offer-{uuid.uuid4().hex[:8]}")
    asset_id: str
    policy: Policy
    provider_id: str


class ContractNegotiation(BaseModel):
    """
    Tracks the contract negotiation state machine.

    Negotiation flow:
    Consumer → REQUESTED → Provider reviews
    Provider → OFFERED → Consumer reviews offer
    Consumer → AGREED → Both parties agree
    Both → VERIFIED → Technical verification
    Both → FINALIZED → Contract is active

    Either party can move to TERMINATED at any point.
    """
    id: str = Field(default_factory=lambda: f"negotiation-{uuid.uuid4().hex[:8]}")
    state: NegotiationState = NegotiationState.REQUESTED
    provider_id: str
    consumer_id: str
    asset_id: str
    offer: Optional[ContractOffer] = None
    agreement: Optional["ContractAgreement"] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    state_history: list[dict] = []


class ContractAgreement(BaseModel):
    """
    Final agreement after successful negotiation.

    This is the binding contract that authorizes data transfer.
    """
    id: str = Field(default_factory=lambda: f"agreement-{uuid.uuid4().hex[:8]}")
    negotiation_id: str
    asset_id: str
    policy: Policy
    provider_id: str
    consumer_id: str
    signing_date: datetime = Field(default_factory=datetime.utcnow)


class TransferProcess(BaseModel):
    """
    Tracks data transfer state.

    After a contract is agreed, the actual data transfer is managed
    through this process, ensuring the transfer complies with the agreement.
    """
    id: str = Field(default_factory=lambda: f"transfer-{uuid.uuid4().hex[:8]}")
    state: TransferState = TransferState.REQUESTED
    agreement_id: str
    asset_id: str
    provider_id: str
    consumer_id: str
    data_destination: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    transferred_data: Optional[dict] = None


class ConnectorInfo(BaseModel):
    """Information about a connector participant."""
    id: str
    name: str
    description: str
    connector_type: str  # "provider" or "consumer"
    endpoint: str
    status: str = "healthy"


# Request/Response models for API endpoints

class NegotiationRequest(BaseModel):
    """Request to initiate a contract negotiation."""
    consumer_id: str
    asset_id: str
    offer_id: Optional[str] = None


class TransferRequest(BaseModel):
    """Request to initiate a data transfer."""
    agreement_id: str
    data_destination: Optional[str] = None


class PolicyEvaluationResult(BaseModel):
    """Result of policy evaluation."""
    allowed: bool
    reason: Optional[str] = None
    evaluated_constraints: list[dict] = []


# Update forward references
DatasetEntry.model_rebuild()
ContractNegotiation.model_rebuild()
