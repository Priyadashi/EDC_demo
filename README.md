# Automotive EDC Demo

A lightweight demonstration of Eclipse Dataspace Connector (EDC) principles for sovereign data exchange in the automotive industry. This demo simulates the Tractus-X/Catena-X approach to secure data sharing between automotive partners.

## 🚀 Quick Start

### Local Development (Docker)

```bash
# Start all services
docker-compose up --build

# Open the demo UI
open http://localhost:3000
```

### Cloud Deployment (Google Cloud Run)

```bash
# Deploy to Cloud Run
./deploy/deploy.sh YOUR_PROJECT_ID

# Follow the URLs printed after deployment
```

## 📋 What This Demo Shows

This demo illustrates the core concepts of sovereign data exchange:

1. **Catalog Browsing** - Consumer discovers available data assets
2. **Policy-Based Access** - Automatic evaluation of access rights
3. **Contract Negotiation** - Formal agreement before data transfer
4. **Secure Data Transfer** - Data flows only after contract

## 🏗️ Architecture

```
┌─────────────────┐         ┌─────────────────┐
│  Provider EDC   │◄───────►│  Consumer EDC   │
│  (OEM)          │  DSP    │  (Tier-1)       │
│                 │         │                 │
│  • Catalog API  │         │  • Catalog Fetch│
│  • Contract API │         │  • Negotiation  │
│  • Transfer API │         │  • Data Receive │
└─────────────────┘         └─────────────────┘
        │                           │
        ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  Sample Data    │         │  Received Data  │
│  (Parts, QA)    │         │                 │
└─────────────────┘         └─────────────────┘

┌─────────────────────────────────────────────┐
│              Demo Web UI                     │
│  Visual interface for the complete flow     │
└─────────────────────────────────────────────┘
```

## 📁 Project Structure

```
automotive-edc-demo/
├── provider-connector/     # OEM data provider (FastAPI)
│   ├── main.py
│   ├── catalog.py
│   ├── contracts.py
│   ├── transfers.py
│   └── Dockerfile
├── consumer-connector/     # Tier-1 supplier (FastAPI)
│   ├── main.py
│   ├── catalog.py
│   ├── negotiations.py
│   ├── transfers.py
│   └── Dockerfile
├── demo-ui/               # React dashboard
│   ├── src/
│   └── Dockerfile
├── shared/                # Common code
│   ├── models.py
│   ├── policies.py
│   └── dsp_protocol.py
├── sample-data/           # Automotive datasets
│   ├── part-catalog.json
│   ├── quality-data.json
│   └── traceability-data.json
├── deploy/                # Deployment configs
│   ├── cloudbuild.yaml
│   └── deploy.sh
├── docs/                  # Documentation
│   ├── SETUP.md
│   ├── DEMO_SCRIPT.md
│   └── ARCHITECTURE.md
└── docker-compose.yml     # Local development
```

## 🎯 Key Features

### Data Sovereignty
- Providers maintain control through policies
- Access requires explicit contract agreement
- Complete audit trail of all operations

### Policy Enforcement
- Automatic evaluation of consumer attributes
- Support for multiple constraint types
- Pre-built automotive industry policies

### Realistic Automotive Data
- Vehicle part catalogs
- Quality metrics and supplier performance
- Battery traceability for compliance

## 📖 Documentation

- [Setup Guide](docs/SETUP.md) - Installation and deployment
- [Demo Script](docs/DEMO_SCRIPT.md) - Presentation walkthrough
- [Architecture](docs/ARCHITECTURE.md) - Technical details

## 🔧 API Documentation

When running, access Swagger docs at:
- Provider: http://localhost:8080/docs
- Consumer: http://localhost:8081/docs

## 💡 Sample Data

The demo includes realistic automotive data:

| Dataset | Description |
|---------|-------------|
| Part Catalog | 2024 EV parts with specifications |
| Quality Metrics | Q4 supplier performance data |
| Traceability | Battery component origins |

## 🌐 Cloud Run Free Tier

This demo is designed to stay within Google Cloud Run's free tier:
- 180,000 vCPU-seconds/month
- 360,000 GiB-seconds/month
- 2 million requests/month
- Scale to zero when idle

## 🔗 Related Projects

- [Eclipse EDC](https://github.com/eclipse-edc/Connector) - The real EDC
- [Tractus-X EDC](https://github.com/eclipse-tractusx/tractusx-edc) - Automotive implementation
- [Catena-X](https://catena-x.net) - Automotive data ecosystem

## 📝 License

This demo is provided as-is for educational purposes.

## 🤝 Contributing

Contributions welcome! Please read the architecture documentation first.

---

**Note**: This is a simulation for demonstration purposes. For production use, deploy the actual [Eclipse Dataspace Connector](https://github.com/eclipse-edc/Connector).
