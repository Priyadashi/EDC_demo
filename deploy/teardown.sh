#!/bin/bash
#
# EDC Demo Teardown Script
# Remove all deployed resources
#
# Usage: ./teardown.sh [PROJECT_ID] [REGION]
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ID=${1:-$(gcloud config get-value project 2>/dev/null)}
REGION=${2:-"us-central1"}

echo -e "${YELLOW}==========================================${NC}"
echo -e "${YELLOW}   Automotive EDC Demo Teardown${NC}"
echo -e "${YELLOW}==========================================${NC}"
echo ""
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""
echo -e "${RED}WARNING: This will delete all EDC demo resources!${NC}"
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo -e "${YELLOW}Deleting Cloud Run services...${NC}"

# Delete services (ignore errors if they don't exist)
gcloud run services delete edc-demo-ui --region=$REGION --quiet 2>/dev/null || true
gcloud run services delete edc-consumer --region=$REGION --quiet 2>/dev/null || true
gcloud run services delete edc-provider --region=$REGION --quiet 2>/dev/null || true

echo ""
echo -e "${YELLOW}Deleting container images...${NC}"

# Delete images (ignore errors)
gcloud container images delete gcr.io/$PROJECT_ID/edc-demo-ui --force-delete-tags --quiet 2>/dev/null || true
gcloud container images delete gcr.io/$PROJECT_ID/edc-consumer --force-delete-tags --quiet 2>/dev/null || true
gcloud container images delete gcr.io/$PROJECT_ID/edc-provider --force-delete-tags --quiet 2>/dev/null || true

echo ""
echo -e "${GREEN}==========================================${NC}"
echo -e "${GREEN}   Teardown Complete!${NC}"
echo -e "${GREEN}==========================================${NC}"
echo ""
echo "All EDC demo resources have been removed."
