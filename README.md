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

### Prerequisites

1. **AWS Account** with appropriate permissions
2. **Pulumi** installed: `pip install pulumi`
3. **GitHub Account** with repository access
4. **AWS Credentials** configured or use OIDC

### Local Deployment (Development)

```bash
# Install Pulumi and dependencies
pip install pulumi pulumi-aws

# Navigate to infrastructure directory
cd infrastructure

# Set up stack
pulumi stack init dev

# Configure AWS region (optional, defaults to us-east-1)
pulumi config set aws:region us-east-1

# Deploy
pulumi up

# Get outputs
pulumi stack output website_url         # Your website URL
pulumi stack output bucket_name         # S3 bucket name
```

### GitHub Actions Automated Deployment

#### Set up AWS IAM Role for OIDC

1. **Create IAM Role** in AWS Console:
   - Go to IAM → Roles → Create Role
   - Trust entity type: Web identity
   - Provider: Token.actions.githubusercontent.com
   - Audience: `sts.amazonaws.com`
   - Subject: `repo:YOUR_GITHUB_ORG/macro-live-data-viewer:ref:refs/heads/main`

2. **Attach Policies** to the role:
   - S3 full access: `AmazonS3FullAccess`
   - Or create custom policy (see below)

**Custom IAM Policy** (recommended):
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
        "s3:DeleteObject*"
      ],
      "Resource": "arn:aws:s3:::macro-live-data-viewer*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:GetRole",
        "iam:CreateRole",
        "iam:PutRolePolicy",
        "iam:GetRolePolicy"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Set GitHub Secrets

1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add the following secrets:

   - `AWS_ROLE_ARN`: `arn:aws:iam::YOUR_ACCOUNT_ID:role/YourGitHubActionsRole`
   - `PULUMI_ACCESS_TOKEN`: Generate from https://app.pulumi.com/account/tokens
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
- Verify IAM role has correct policies
- Check AWS_ROLE_ARN is correct
- Ensure OIDC provider is configured

**Website not updating after push:**
- Check GitHub Actions workflow logs for S3 sync errors
- Verify S3 bucket and files in AWS Console
- Clear browser cache
- Wait for TTL expiration (default 3600s for HTML)

**Data not updating at night:**
- Check GitHub Actions workflow logs
- Verify PULUMI_ACCESS_TOKEN is valid
- Check AWS credentials haven't expired

### Destruction

To remove all AWS resources:

```bash
cd infrastructure
pulumi destroy --yes
```

This will delete:
- S3 bucket and all contents
