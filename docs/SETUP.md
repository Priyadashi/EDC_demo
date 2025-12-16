# EDC Demo Setup Guide

This guide will help you deploy the Automotive EDC Demo to Google Cloud Run. No programming experience required!

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Google Cloud Setup](#google-cloud-setup)
3. [Local Development](#local-development)
4. [Cloud Deployment](#cloud-deployment)
5. [Troubleshooting](#troubleshooting)
6. [Cost Management](#cost-management)

---

## Prerequisites

Before you begin, you'll need:

### Required Accounts
- **Google Cloud Account**: Sign up at [cloud.google.com](https://cloud.google.com)
  - Free tier includes $300 credit for new users
  - Cloud Run has a generous always-free tier

### Required Software
- **Google Cloud CLI (gcloud)**: [Installation Guide](https://cloud.google.com/sdk/docs/install)
- **Docker Desktop** (for local testing): [Download](https://www.docker.com/products/docker-desktop)
- **Git**: [Download](https://git-scm.com/downloads)

---

## Google Cloud Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "edc-demo")
5. Click "Create"
6. Wait for the project to be created, then select it

### Step 2: Enable Billing

> **Note**: Billing must be enabled, but this demo stays within free tier limits.

1. Go to [Billing](https://console.cloud.google.com/billing)
2. Link a billing account to your project
3. The demo is designed to stay within free tier limits

### Step 3: Install and Configure gcloud

Open a terminal and run:

```bash
# Install gcloud if not already installed
# Follow instructions at: https://cloud.google.com/sdk/docs/install

# Login to your Google account
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Verify configuration
gcloud config list
```

---

## Local Development

### Option A: Using Docker Compose (Recommended)

This is the easiest way to run the demo locally.

```bash
# Clone or navigate to the project
cd automotive-edc-demo

# Start all services
docker-compose up --build

# Access the demo:
# - Demo UI: http://localhost:3000
# - Provider API: http://localhost:8080
# - Consumer API: http://localhost:8081
```

To stop the services:
```bash
docker-compose down
```

### Option B: Running Services Individually

If you prefer to run services without Docker:

#### Provider Connector
```bash
cd provider-connector
pip install -r requirements.txt
python main.py
# Runs on http://localhost:8080
```

#### Consumer Connector
```bash
cd consumer-connector
pip install -r requirements.txt
PROVIDER_URL=http://localhost:8080 python main.py
# Runs on http://localhost:8081
```

#### Demo UI
```bash
cd demo-ui
npm install
npm run dev
# Runs on http://localhost:3000
```

---

## Cloud Deployment

### Quick Deploy (Recommended)

We've created a simple script that handles everything:

```bash
# Make the script executable
chmod +x deploy/deploy.sh

# Run deployment
./deploy/deploy.sh YOUR_PROJECT_ID

# Or let it detect your project automatically
./deploy/deploy.sh
```

The script will:
1. Enable required Google Cloud APIs
2. Build all Docker images
3. Push images to Google Container Registry
4. Deploy to Cloud Run
5. Configure environment variables
6. Print your demo URLs

### Manual Deployment

If you prefer manual control:

```bash
# Set your project
export PROJECT_ID=your-project-id
export REGION=us-central1

# Enable APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com

# Submit build
gcloud builds submit --config=deploy/cloudbuild.yaml --substitutions=_REGION=$REGION
```

### After Deployment

Your demo will be available at three URLs (shown after deployment):

1. **Demo UI**: The main interface for running the demo
2. **Provider API**: The OEM connector (view at `/docs` for API documentation)
3. **Consumer API**: The Tier-1 Supplier connector (view at `/docs` for API documentation)

---

## Troubleshooting

### Common Issues

#### "Permission denied" errors
```bash
# Make sure you're authenticated
gcloud auth login
gcloud auth application-default login

# Verify project permissions
gcloud projects get-iam-policy YOUR_PROJECT_ID
```

#### "API not enabled" errors
```bash
# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

#### Docker build fails
```bash
# Clean up Docker
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

#### Cloud Run deployment fails
- Check [Cloud Build logs](https://console.cloud.google.com/cloud-build/builds)
- Verify project billing is enabled
- Ensure you have the Cloud Run Admin role

#### UI can't connect to APIs
- Check CORS settings in the API deployments
- Verify the API URLs are correct in the UI environment
- Check Cloud Run logs for errors

### Getting Help

1. Check Cloud Run logs: [Cloud Run Console](https://console.cloud.google.com/run)
2. Check build logs: [Cloud Build Console](https://console.cloud.google.com/cloud-build)
3. Review service status: `gcloud run services list`

---

## Cost Management

### Free Tier Limits

Google Cloud Run free tier includes (per month):
- 180,000 vCPU-seconds
- 360,000 GiB-seconds
- 2 million requests
- 1 GiB egress (North America)

### This Demo's Usage

- **Scale to Zero**: Services shut down when not in use (no cost)
- **Small Containers**: 256MB memory, 1 vCPU max
- **Minimal Requests**: Demo usage is well within free limits

### Setting Up Billing Alerts

1. Go to [Billing Budgets](https://console.cloud.google.com/billing/budgets)
2. Click "Create Budget"
3. Set a budget (e.g., $5/month for alerts)
4. Configure alert thresholds (50%, 90%, 100%)

### Cleaning Up

To remove all resources and stop any charges:

```bash
chmod +x deploy/teardown.sh
./deploy/teardown.sh YOUR_PROJECT_ID
```

Or manually:
```bash
gcloud run services delete edc-demo-ui --region=us-central1 --quiet
gcloud run services delete edc-consumer --region=us-central1 --quiet
gcloud run services delete edc-provider --region=us-central1 --quiet
```

---

## Next Steps

After deployment:

1. Open the Demo UI URL in your browser
2. Read [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) for a guided walkthrough
3. Review [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system

## Support

For issues with this demo:
- Check the troubleshooting section above
- Review the architecture documentation
- Examine the API documentation at `/docs` on each service
