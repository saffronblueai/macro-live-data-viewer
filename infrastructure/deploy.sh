#!/bin/bash
# Pulumi Infrastructure Setup Helper
# This script helps initialize and deploy the infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Macro Live Data Viewer - Deploy Setup  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"

if ! command -v pulumi &> /dev/null; then
    echo -e "${RED}✗ Pulumi CLI is not installed${NC}"
    echo "Install with: curl -fsSL https://get.pulumi.com | sh"
    exit 1
fi
echo -e "${GREEN}✓ Pulumi found: $(pulumi version)${NC}"

if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}⚠ AWS CLI is not installed${NC}"
    echo "Installing AWS CLI..."
    pip install awscli
fi
echo -e "${GREEN}✓ AWS CLI found${NC}"

echo ""

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}✗ AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS credentials valid (Account: $ACCOUNT_ID)${NC}"

echo ""

# Navigate to infrastructure directory
cd infrastructure

echo -e "${YELLOW}Setting up Pulumi stack...${NC}"

# Ask for stack name
read -p "Enter stack name (default: dev): " STACK_NAME
STACK_NAME=${STACK_NAME:-dev}

# Ask for AWS region
read -p "Enter AWS region (default: us-east-1): " REGION
REGION=${REGION:-us-east-1}

# Initialize stack
if pulumi stack select $STACK_NAME 2>/dev/null; then
    echo -e "${GREEN}✓ Using existing stack: $STACK_NAME${NC}"
else
    echo -e "${YELLOW}Creating new stack: $STACK_NAME${NC}"
    pulumi stack init $STACK_NAME
fi

# Set configuration
echo -e "${YELLOW}Configuring stack...${NC}"
pulumi config set aws:region $REGION
echo -e "${GREEN}✓ AWS region set to: $REGION${NC}"

# Ask if they want to preview first
echo ""
read -p "Would you like to preview the deployment? (y/n): " PREVIEW
if [[ $PREVIEW == "y" || $PREVIEW == "Y" ]]; then
    echo -e "${YELLOW}Running pulumi preview...${NC}"
    pulumi preview --diff
    echo ""
fi

# Ask if they want to deploy
read -p "Ready to deploy? (y/n): " DEPLOY
if [[ $DEPLOY != "y" && $DEPLOY != "Y" ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Deploy
echo -e "${YELLOW}Deploying infrastructure...${NC}"
pulumi up --yes

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Deployment Successful!                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""

# Get outputs
echo -e "${YELLOW}Deployment Information:${NC}"
echo -e "${GREEN}S3 Bucket:${NC} $(pulumi stack output bucket_name)"
echo -e "${GREEN}Website URL:${NC} $(pulumi stack output website_url)"

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test your website: $(pulumi stack output website_url)"
echo "2. Set up GitHub secrets for CI/CD (see DEPLOYMENT.md)"
echo "3. Push to GitHub to trigger automated deployment"
echo ""
echo "For more information, see: DEPLOYMENT.md"
