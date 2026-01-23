# Quick Reference Guide

Fast commands for common tasks.

## Initial Setup

```bash
# One-time setup
cd infrastructure
python3 deploy.py  # Interactive setup wizard
# OR
bash deploy.sh     # Bash version

# Verify deployment
open $(pulumi stack output website_url)
```

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r infrastructure/requirements.txt

# Run locally
python server.py

# Fetch data manually
python fetch_data.py
python fetch_sentiment.py
```

## Deployment Operations

```bash
cd infrastructure

# Preview changes
pulumi preview

# Deploy
pulumi up

# Destroy (cleanup)
pulumi destroy

# View stack information
pulumi stack output
pulumi stack history

# Select different stack
pulumi stack select prod
pulumi stack ls
```

## Data Management

```bash
# Full fetch (overwrites last 60 days)
python fetch_data.py
python fetch_sentiment.py

# Incremental update (adds new data)
python fetch_data.py update
python fetch_sentiment.py --update-all

# Regenerate data.js only
python fetch_data.py generate
```

## AWS S3 Operations

```bash
# List bucket contents
aws s3 ls s3://macro-live-data-viewer-dev-bucket/

# Download all files
aws s3 sync s3://macro-live-data-viewer-dev-bucket/ ./

# Upload specific file
aws s3 cp data.js s3://macro-live-data-viewer-dev-bucket/data.js

# Get bucket info
aws s3api head-bucket --bucket macro-live-data-viewer-dev-bucket
```

## S3 Operations

```bash
# List all objects in bucket
aws s3 ls s3://macro-live-data-viewer-dev-bucket/ --recursive

# Sync local directory to S3
aws s3 sync ./ s3://macro-live-data-viewer-dev-bucket/ --exclude ".*"

# Delete all objects from bucket
aws s3 rm s3://macro-live-data-viewer-dev-bucket/ --recursive
```

## GitHub Secrets Management

```bash
# View GitHub CLI (if installed)
gh secret list

# Set via GitHub web UI:
# Settings → Secrets and variables → Actions → New secret
```

## Troubleshooting

```bash
# Check Pulumi state
pulumi stack output
pulumi stack export

# View deployment history
pulumi history

# Get detailed error info
pulumi up --diff --verbose

# Clear Pulumi cache
rm -rf .pulumi/

# Test AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls
```

## Monitoring

```bash
# Monitor GitHub Actions
gh run list -R YOUR_REPO/macro-live-data-viewer
gh run view RUN_ID -R YOUR_REPO/macro-live-data-viewer

# Check S3 metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name NumberOfObjects \
  --dimensions Name=BucketName,Value=macro-live-data-viewer-dev-bucket \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 86400 \
  --statistics Average
```

## Cost Optimization

```bash
# Check S3 storage
aws s3api list-objects-v2 --bucket macro-live-data-viewer-dev-bucket \
  --output table \
  --query 'Contents[].{Key:Key,Size:Size}'

# Estimate S3 costs
# Use AWS Cost Calculator: https://calculator.aws/
```

## Documentation

- Full deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Project README: [README.md](README.md)
- Pulumi docs: https://www.pulumi.com/docs/
- AWS S3 docs: https://docs.aws.amazon.com/s3/
- GitHub Actions: https://docs.github.com/en/actions

## Environment Variables

```bash
# For local development
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# For Pulumi
export PULUMI_STACK_NAME=dev
export PULUMI_SKIP_UPDATE_CHECK=true
```

## Stack Configuration Files

- `infrastructure/Pulumi.yaml` - Project definition
- `infrastructure/Pulumi.dev.yaml` - Dev stack config
- `.github/workflows/deploy.yml` - CI/CD deployment
- `.github/workflows/nightly-data-update.yml` - Scheduled data updates
