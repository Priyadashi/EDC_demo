# EDC Demo Architecture

This document explains the architecture of the Automotive EDC Demo and how it maps to real Eclipse Dataspace Connector concepts.

## Table of Contents

1. [Overview](#overview)
2. [Component Architecture](#component-architecture)
3. [Data Models](#data-models)
4. [Protocol Flow](#protocol-flow)
5. [Policy System](#policy-system)
6. [Mapping to Real EDC](#mapping-to-real-edc)

---

## Overview

This demo implements a **simulated** Eclipse Dataspace Connector to demonstrate sovereign data exchange principles. It follows the Dataspace Protocol (DSP) specification used by Catena-X/Tractus-X.

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Python/FastAPI | Lightweight, easy to understand, fast cold starts |
| In-memory state | Simple, no database costs, acceptable for demo |
| Simulated EDC | Focus on concepts rather than full EDC complexity |
| React UI | Modern, interactive, good for presentations |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Google Cloud Run                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐              ┌──────────────────┐             │
│  │  Provider EDC    │              │  Consumer EDC    │             │
│  │  (Port 8080)     │◄────────────►│  (Port 8081)     │             │
│  │                  │   HTTP/REST  │                  │             │
│  │  ┌────────────┐  │              │  ┌────────────┐  │             │
│  │  │ Catalog API│  │              │  │Cat. Browser│  │             │
│  │  ├────────────┤  │              │  ├────────────┤  │             │
│  │  │Contract API│  │              │  │Neg. Client │  │             │
│  │  ├────────────┤  │              │  ├────────────┤  │             │
│  │  │Transfer API│  │              │  │Trans. Recv │  │             │
│  │  ├────────────┤  │              │  ├────────────┤  │             │
│  │  │ Data Plane │  │              │  │ Data Store │  │             │
│  │  └────────────┘  │              │  └────────────┘  │             │
│  └────────┬─────────┘              └────────┬─────────┘             │
│           │                                  │                       │
│           ▼                                  ▼                       │
│  ┌──────────────────┐              ┌──────────────────┐             │
│  │  Sample Data     │              │  Received Data   │             │
│  │  (JSON Files)    │              │  (In-Memory)     │             │
│  └──────────────────┘              └──────────────────┘             │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                    Demo Web UI (Port 3000)                  │     │
│  │  React Application with Tailwind CSS                        │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Provider Connector

The provider (OEM) offers data assets to the dataspace.

```
provider-connector/
├── main.py           # FastAPI application entry point
├── catalog.py        # Catalog Protocol implementation
├── contracts.py      # Contract Negotiation Protocol
├── transfers.py      # Transfer Process Protocol
├── data_plane.py     # Data serving endpoints
├── store.py          # In-memory state management
└── requirements.txt  # Python dependencies
```

#### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/catalog` | GET | Get full DSP catalog |
| `/api/catalog/datasets` | GET | List datasets (simplified) |
| `/api/catalog/datasets/{id}` | GET | Get dataset details |
| `/api/negotiations` | POST | Start negotiation |
| `/api/negotiations/{id}` | GET | Get negotiation status |
| `/api/negotiations/{id}/offer` | POST | Provider makes offer |
| `/api/negotiations/{id}/agree` | POST | Consumer agrees |
| `/api/negotiations/{id}/verify` | POST | Verify agreement |
| `/api/negotiations/{id}/finalize` | POST | Create contract |
| `/api/transfers` | POST | Initiate transfer |
| `/api/transfers/{id}/start` | POST | Start data transfer |
| `/api/transfers/{id}/complete` | POST | Complete transfer |
| `/api/transfers/{id}/data` | GET | Get transferred data |

### Consumer Connector

The consumer (Tier-1 Supplier) requests data from providers.

```
consumer-connector/
├── main.py           # FastAPI application entry point
├── catalog.py        # Catalog fetching and caching
├── negotiations.py   # Negotiation client
├── transfers.py      # Transfer receiving
├── store.py          # In-memory state + identity
└── requirements.txt  # Python dependencies
```

#### Consumer Identity

The consumer has identity attributes used for policy evaluation:

```python
{
    "consumer_id": "consumer-tierone-supplier",
    "company_name": "TierOne Electronics GmbH",
    "partner_type": "tier1_supplier",
    "region": "EU",
    "certifications": ["TISAX", "ISO27001", "IATF16949"],
    "purpose": "quality_analysis"
}
```

### Demo Web UI

React single-page application for visualization.

```
demo-ui/
├── src/
│   ├── App.jsx                    # Main application
│   ├── components/
│   │   ├── Header.jsx             # App header
│   │   ├── ConnectorStatus.jsx    # Status cards
│   │   ├── CatalogBrowser.jsx     # Dataset browsing
│   │   ├── NegotiationFlow.jsx    # Negotiation wizard
│   │   ├── TransferMonitor.jsx    # Transfer progress
│   │   ├── DataViewer.jsx         # Received data display
│   │   └── ArchitectureDiagram.jsx # Visual diagram
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Tailwind styles
└── package.json
```

### Shared Components

Common code used by both connectors.

```
shared/
├── models.py         # Pydantic data models
├── policies.py       # Policy engine + templates
├── dsp_protocol.py   # DSP message types
└── __init__.py
```

---

## Data Models

### Core Models

```python
# Asset - A data offering
class Asset:
    id: str                    # Unique identifier
    name: str                  # Human-readable name
    description: str           # Description
    content_type: str          # MIME type
    properties: dict           # Custom metadata

# Policy - Access control rules
class Policy:
    id: str
    permissions: list[Permission]   # What's allowed
    prohibitions: list[Prohibition] # What's forbidden
    obligations: list[Obligation]   # What's required

# ContractNegotiation - State machine
class ContractNegotiation:
    id: str
    state: NegotiationState    # REQUESTED → FINALIZED
    provider_id: str
    consumer_id: str
    asset_id: str
    agreement: ContractAgreement | None

# TransferProcess - Data movement
class TransferProcess:
    id: str
    state: TransferState       # REQUESTED → COMPLETED
    agreement_id: str
    data: dict | None          # The actual data
```

### State Machines

#### Negotiation States

```
REQUESTED → OFFERED → AGREED → VERIFIED → FINALIZED
     ↓         ↓         ↓         ↓
  TERMINATED (can happen at any state)
```

#### Transfer States

```
REQUESTED → STARTED → COMPLETED
     ↓          ↓
  TERMINATED (can happen before completion)
```

---

## Protocol Flow

### Complete Data Exchange Flow

```
Consumer                    Provider
   │                           │
   │  1. GET /api/catalog      │
   │ ─────────────────────────>│
   │                           │
   │     Catalog Response      │
   │ <─────────────────────────│
   │                           │
   │  2. POST /negotiations    │
   │ ─────────────────────────>│
   │                           │
   │     Negotiation Created   │
   │ <─────────────────────────│
   │                           │
   │  3. POST .../offer        │
   │ ─────────────────────────>│
   │     (Policy Evaluation)   │
   │     OFFERED/TERMINATED    │
   │ <─────────────────────────│
   │                           │
   │  4. POST .../agree        │
   │ ─────────────────────────>│
   │     AGREED                │
   │ <─────────────────────────│
   │                           │
   │  5. POST .../verify       │
   │ ─────────────────────────>│
   │     VERIFIED              │
   │ <─────────────────────────│
   │                           │
   │  6. POST .../finalize     │
   │ ─────────────────────────>│
   │     Agreement Created     │
   │ <─────────────────────────│
   │                           │
   │  7. POST /transfers       │
   │ ─────────────────────────>│
   │     Transfer Created      │
   │ <─────────────────────────│
   │                           │
   │  8. POST .../start        │
   │ ─────────────────────────>│
   │     STARTED               │
   │ <─────────────────────────│
   │                           │
   │  9. POST .../complete     │
   │ ─────────────────────────>│
   │     COMPLETED + Data      │
   │ <─────────────────────────│
   │                           │
```

---

## Policy System

### Policy Structure (ODRL-based)

```python
Policy = {
    "permissions": [
        {
            "action": "USE",
            "constraints": [
                {
                    "leftOperand": "partner_type",
                    "operator": "eq",
                    "rightOperand": "tier1_supplier"
                }
            ]
        }
    ],
    "prohibitions": [
        {"action": "DISTRIBUTE"}
    ]
}
```

### Supported Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `eq` | Equals | `partner_type eq tier1_supplier` |
| `neq` | Not equals | `region neq APAC` |
| `in` | In list | `region in [EU, NA]` |
| `gt` | Greater than | `clearance_level gt 3` |
| `lt` | Less than | `risk_score lt 5` |
| `contains` | Contains | `certifications contains TISAX` |
| `has_any` | Has any of | `certifications has_any [TISAX, ISO27001]` |

### Policy Templates

The demo includes these pre-configured policies:

| Policy ID | Description |
|-----------|-------------|
| `tier1-only` | Only Tier-1 suppliers can access |
| `certified-partners` | Requires TISAX or ISO27001 certification |
| `eu-region` | Only EU/EEA partners |
| `quality-data` | Tier-1/Tier-2 for quality analysis purpose |
| `traceability` | Requires IATF16949 certification |
| `open-access` | No restrictions (USE allowed) |

---

## Mapping to Real EDC

### What This Demo Simulates

| Demo Component | Real EDC Component |
|----------------|-------------------|
| Provider Connector | EDC Control Plane + Data Plane |
| Consumer Connector | EDC Control Plane + Data Plane |
| In-memory store | PostgreSQL + Vault |
| JSON policies | ODRL policies |
| HTTP transfers | EDC Data Plane protocols |
| Sample data files | S3, Azure Blob, HTTP endpoints |

### What This Demo Simplifies

| Aspect | Demo | Production EDC |
|--------|------|----------------|
| Identity | Static attributes | Verifiable Credentials / DAPS |
| Policies | Pre-defined | Dynamic ODRL policies |
| Data plane | HTTP push | S3, HTTP, streaming |
| State | In-memory | Persistent database |
| Security | None | OAuth2, TLS, signatures |
| Scale | Single instance | Distributed |

### Extending to Production

To move from this demo to production EDC:

1. **Deploy Real EDC**: Use [Tractus-X EDC](https://github.com/eclipse-tractusx/tractusx-edc)
2. **Configure Identity**: Integrate with DAPS or Verifiable Credentials
3. **Add Data Planes**: Configure appropriate data transfer protocols
4. **Persistent Storage**: Connect PostgreSQL and Vault
5. **Policy Management**: Create dynamic ODRL policies
6. **Security**: Add TLS, OAuth2, and token validation

---

## Sample Data

### Available Datasets

#### Part Catalog (`part-catalog.json`)
- Complete parts catalog for 2024 EV model year
- Categories: Powertrain, Battery, Chassis
- Includes specifications, suppliers, applicability

#### Quality Metrics (`quality-data.json`)
- Q4 2024 supplier quality performance
- PPM rates, delivery performance, certifications
- Corrective actions and trends

#### Traceability Data (`traceability-data.json`)
- Battery component traceability
- Raw material origins (lithium, cobalt, nickel)
- Carbon footprint calculations
- Regulatory compliance (EU Battery Regulation)

---

## Deployment Architecture

### Cloud Run Configuration

Each service is deployed with:
- **Memory**: 256 MiB
- **CPU**: 1 vCPU
- **Min instances**: 0 (scale to zero)
- **Max instances**: 2
- **Timeout**: 60 seconds

### Cost Optimization

- Scale-to-zero eliminates idle costs
- Small containers minimize resource usage
- Request-based billing (not instance-based)
- All within Cloud Run free tier for demo usage

---

## Future Enhancements

Potential improvements for production use:

1. **Persistent State**: Add Cloud SQL or Firestore
2. **Authentication**: Add OAuth2/OIDC
3. **Real EDC Integration**: Replace simulation with actual EDC
4. **More Data Planes**: S3, Azure Blob, streaming
5. **Policy Editor**: UI for creating custom policies
6. **Usage Enforcement**: Post-transfer policy monitoring
7. **Multi-provider**: Support multiple data providers
