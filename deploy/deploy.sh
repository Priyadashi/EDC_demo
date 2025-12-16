#!/bin/bash
#
# EDC Demo Deployment Script
# Deploy to Google Cloud Run
#
# Usage: ./deploy.sh [PROJECT_ID] [REGION]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${1:-""}
REGION=${2:-"us-central1"}

echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   Automotive EDC Demo Deployment${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""

# Check if PROJECT_ID is provided
if [ -z "$PROJECT_ID" ]; then
    echo -e "${YELLOW}No PROJECT_ID provided. Attempting to detect...${NC}"
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

    if [ -z "$PROJECT_ID" ]; then
        echo -e "${RED}Error: No PROJECT_ID found. Please provide it as an argument.${NC}"
        echo "Usage: ./deploy.sh PROJECT_ID [REGION]"
        exit 1
    fi
fi

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed.${NC}"
    echo "Please install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set the project
echo -e "${YELLOW}Setting active project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}Enabling required APIs...${NC}"
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

echo ""
echo -e "${YELLOW}Starting Cloud Build deployment...${NC}"
echo "This may take 10-15 minutes on first deployment."
echo ""

# Submit the build
gcloud builds submit --config=deploy/cloudbuild.yaml --substitutions=_REGION=$REGION

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   Deployment Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""

# Get and display URLs
echo -e "${GREEN}Your EDC Demo is now live!${NC}"
echo ""
echo "Demo UI:"
gcloud run services describe edc-demo-ui --region=$REGION --format='value(status.url)'
echo ""
echo "Provider API:"
gcloud run services describe edc-provider --region=$REGION --format='value(status.url)'
echo ""
echo "Consumer API:"
gcloud run services describe edc-consumer --region=$REGION --format='value(status.url)'
echo ""

echo -e "${YELLOW}Cost Information:${NC}"
echo "- All services scale to zero when idle (no cost when not in use)"
echo "- Expected cost within free tier for demo usage"
echo "- Set up billing alerts at: https://console.cloud.google.com/billing"
echo ""
