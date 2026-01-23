# Macro Data Dashboard

A dashboard displaying global macro data: bond yields, stock indices, currencies, and sentiment.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Fetch all data and start server
python fetch_data.py
python fetch_sentiment.py
python server.py
```

Open http://127.0.0.1:5000 in your browser.

---

## Updating Data

### Market Data (bonds, stocks, currencies)

```bash
# Full refresh (overwrites last 60 days)
python fetch_data.py

# Incremental update (adds new data only)
python fetch_data.py update

# Regenerate data.js from existing CSVs (no fetch)
python fetch_data.py generate
```

**Partial fetches:**
```bash
python fetch_data.py bonds    # Bond yields only
python fetch_data.py stocks   # Stocks & currencies only
```

### Sentiment Data

```bash
# Full fetch (international)
python fetch_sentiment.py

# Full fetch (domestic)
python fetch_sentiment.py --index-type DOMESTIC

# Incremental updates
python fetch_sentiment.py --update                          # International
python fetch_sentiment.py --update --index-type DOMESTIC    # Domestic
python fetch_sentiment.py --update-all                      # Both
```

---

## Running the Server

```bash
python server.py                    # Default (localhost:5000)
python server.py --port 8080        # Custom port
python server.py --host 0.0.0.0     # Allow external access
python server.py --refresh          # Refresh data before starting
python server.py --debug            # Auto-reload on file changes
```

**API endpoints:**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Server status & data freshness |
| `/api/refresh` | POST | Trigger data refresh |
| `/api/data` | GET | Get all data as JSON |

---

## Output Files

| File | Description |
|------|-------------|
| `data.js` | Combined data for dashboard |
| `bond_yields_10y.csv` | 10-year bond yields |
| `stock_indices.csv` | Stock index prices |
| `currencies.csv` | Currency rates vs USD |
| `sentiment_data.csv` | International sentiment |
| `sentiment_data_domestic.csv` | Domestic sentiment |

---

## AWS Deployment with Pulumi

This project can be deployed to AWS S3 for static website hosting with automated CI/CD.


### 🔐 Security Features

- ✅ AWS secret key authentication (encrypted in GitHub)
- ✅ Scoped IAM permissions (S3 only)
- ✅ S3 bucket with public read via website hosting
- ✅ Secrets encrypted and masked in GitHub Actions

### 💰 Cost Estimate

**Monthly Cost: ~$0.03 - $0.50**

Breakdown:
- S3 Storage: ~$0.02
- S3 Requests: ~$0.01
- Data Transfer: FREE (mostly covered by free tier)

### Documentation

| File | Purpose |
|------|---------|
| `DEPLOYMENT.md` | Comprehensive step-by-step deployment guide |
| `QUICKSTART.md` | Quick reference for common commands |
| `ARCHITECTURE.md` | System architecture & data flow diagrams |
| `SETUP_SUMMARY.md` | Overview of what was created |
| `PRE_DEPLOYMENT_CHECKLIST.md` | Pre-deployment verification checklist |

### Prerequisites

1. **AWS Account** with IAM user credentials
2. **Pulumi** installed: `pip install pulumi`
3. **GitHub Account** with repository access
4. **AWS Access Key ID and Secret Access Key** for IAM user

### Local Deployment (Development)

```bash
# Install Pulumi and dependencies
pip install pulumi pulumi-aws

# Navigate to infrastructure directory
cd infrastructure

# Set up stack
pulumi stack init dev

# Deploy
pulumi up

# Get outputs
pulumi stack output website_url         # Your website URL
pulumi stack output bucket_name         # S3 bucket name
```

### GitHub Actions Automated Deployment

#### Create AWS IAM User with Access Keys

1. **Create IAM User** in AWS Console:
   - Go to IAM → Users → Create User
   - Username: `github-actions-macro-viewer` (or similar)
   - Uncheck "Provide user access to AWS Management Console"

2. **Create Access Keys**:
   - Select the user, go to Security credentials tab
   - Click "Create access key"
   - Select "Command line interface (CLI)"
   - Copy the Access Key ID and Secret Access Key

3. **Attach Policy to user**:
   - Go to user → Permissions → Add permissions
   - Use policy below (recommended) or `AmazonS3FullAccess`

**Custom IAM Policy** (recommended for minimal permissions):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:GetBucket*",
        "s3:ListBucket*",
        "s3:PutObject*",
        "s3:DeleteObject*",
        "s3:PutBucketWebsite",
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy"
      ],
      "Resource": "arn:aws:s3:::macro-live-data-viewer*"
    }
  ]
}
```

#### Set GitHub Secrets

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add the following secrets:

   - `AWS_ACCESS_KEY_ID`: From IAM user access keys
   - `AWS_SECRET_ACCESS_KEY`: From IAM user access keys
   - `PULUMI_CONFIG_PASSPHRASE`: Any passphrase for Pulumi state encryption

#### Workflows

**1. Deploy Workflow** (`.github/workflows/deploy.yml`)
- Triggers on: `push` to `main` or `develop`, or manual trigger
- Deploys infrastructure and website files to S3
- Commits Pulumi state files for tracking

**2. Nightly Data Update** (`.github/workflows/nightly-data-update.yml`)
- Triggers: Every day at 8 PM UTC (or manual trigger)
- Downloads existing data from S3
- Runs: `python fetch_sentiment.py --update-all` 
- Runs: `python fetch_data.py update`
- Regenerates `data.js`
- Uploads updated files back to S3
- Optionally commits changes back to repository

### Accessing Your Website

After deployment, your website will be available at the S3 website URL output:

```
https://macro-live-data-viewer-bucket.s3-website-us-east-1.amazonaws.com
```

### Managing Stacks

```bash
cd infrastructure

# List stacks
pulumi stack ls

# Select a stack
pulumi stack select dev

# View stack outputs
pulumi stack output

# Destroy infrastructure (careful!)
pulumi destroy
```

### Cost Optimization Tips

- **S3**: Storage costs are minimal for CSV/JS files
- **S3**: First 5GB free tier, then tiered pricing for storage and requests
- **Data Transfer**: Monitor egress costs
- **Consider**: Using AWS free tier when possible

### Monitoring & Logs

- **S3 Bucket**: Check object sizes in AWS Console
- **S3**: View request metrics and storage usage
- **GitHub Actions**: View workflow logs in Actions tab
- **Pulumi**: View deployment history at https://app.pulumi.com

### Troubleshooting

**Deployment fails with permission errors:**
- Verify IAM user has correct S3 policies
- Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are correct
- Verify keys are not expired or revoked in AWS Console

**Website not updating after push:**
- Check GitHub Actions workflow logs for S3 sync errors
- Verify S3 bucket and files in AWS Console
- Clear browser cache
- Wait for TTL expiration (default 3600s for HTML)

**Data not updating at night:**
- Check GitHub Actions workflow logs
- Check AWS credentials haven't expired

### Destruction

To remove all AWS resources:

```bash
cd infrastructure
pulumi destroy --yes
```

This will delete:
- S3 bucket and all contents
