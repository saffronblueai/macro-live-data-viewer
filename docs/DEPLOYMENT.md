# AWS Deployment Guide

This guide provides step-by-step instructions to deploy the Macro Live Data Viewer to AWS using Pulumi and GitHub Actions.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Deployment](#local-deployment)
3. [GitHub Actions Setup](#github-actions-setup)
4. [Verification](#verification)
5. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11+**: [Install from python.org](https://www.python.org/downloads/)
- **Pulumi CLI**: `curl -fsSL https://get.pulumi.com | sh`
- **AWS CLI**: `pip install awscli` or [Install from AWS](https://aws.amazon.com/cli/)
- **Git**: For version control

### AWS Account Setup

1. Create an [AWS Account](https://aws.amazon.com/free/)
2. Create an [IAM User](https://console.aws.amazon.com/iam/) with programmatic access
3. Attach policy `AdministratorAccess` (for initial setup) or use custom policy
4. Download credentials and keep safe

### Pulumi Account (Optional but recommended)

1. Create account at [app.pulumi.com](https://app.pulumi.com)
2. Create new organization
3. Generate access token: Account Settings → Tokens → Create token

---

## Local Deployment

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install infrastructure dependencies
cd infrastructure
pip install -r requirements.txt
```

### Step 2: Configure AWS

```bash
# Configure AWS credentials
aws configure

# Enter when prompted:
# AWS Access Key ID: [your access key]
# AWS Secret Access Key: [your secret key]
# Default region: us-east-1
# Default output format: json
```

Or set environment variables:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

### Step 3: Initialize Pulumi Stack

```bash
cd infrastructure

# Initialize a new stack
pulumi stack init dev

# (Optional) Use Pulumi cloud backend
# pulumi login
```

### Step 4: Configure Stack

```bash
# Set AWS region (optional, defaults to us-east-1)
pulumi config set aws:region us-east-1

# (Optional) Set encryption passphrase for sensitive data
pulumi config set --secret db_password "your-secret-password"
```

### Step 5: Preview Deployment

```bash
# Preview what will be created
pulumi preview
```

You'll see a summary of resources to be created:
- S3 bucket with static website hosting
- S3 bucket policy for public read access
- Website files (HTML, JS, CSV)

### Step 6: Deploy Infrastructure

```bash
# Deploy to AWS
pulumi up

# Review changes and confirm with "yes"
```

After successful deployment, you'll see outputs:

```
Outputs:
  bucket_name                 : macro-live-data-viewer-bucket
  bucket_regional_domain_name : s3-website-us-east-1.amazonaws.com
  website_url                 : https://macro-live-data-viewer-bucket.s3-website-us-east-1.amazonaws.com
```

### Step 7: Access Your Website

```bash
# Get the website URL
pulumi stack output website_url

# Open in browser
open $(pulumi stack output website_url)
```

---

## GitHub Actions Setup

### Step 1: Configure AWS for OIDC

This allows GitHub Actions to authenticate with AWS securely without storing credentials.

#### Create IAM Role

1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. **Identity Providers** → **Create Provider**:
   - Provider type: **OpenID Connect**
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`
   - Click **Get thumbprint** (should auto-populate)
   - Click **Create Provider**

3. **Roles** → **Create Role**:
   - Trust entity type: **Web identity**
   - Identity provider: `token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`
   - Click **Next**
   - Add policy: `AdministratorAccess` (or use custom policy below)
   - Role name: `GitHubActionsRole-macro-live-data-viewer`
   - Create role

#### (Optional) Restrict to your repository

In the role's trust relationship, add condition:

```json
"Condition": {
  "StringEquals": {
    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
  },
  "StringLike": {
    "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_ORG/macro-live-data-viewer:ref:refs/heads/main"
  }
}
```

#### Custom IAM Policy (Recommended)

Create a custom policy with these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3Access",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:GetBucket*",
        "s3:ListBucket*",
        "s3:PutObject*",
        "s3:DeleteObject*",
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy"
      ],
      "Resource": [
        "arn:aws:s3:::macro-live-data-viewer*",
        "arn:aws:s3:::macro-live-data-viewer*/*"
      ]
    },
    {
      "Sid": "IAMAccess",
      "Effect": "Allow",
      "Action": [
        "iam:GetRole",
        "iam:CreateRole",
        "iam:DeleteRole",
        "iam:PutRolePolicy",
        "iam:DeleteRolePolicy",
        "iam:PassRole",
        "iam:GetRolePolicy"
      ],
      "Resource": "arn:aws:iam::*:role/cdk-*"
    },
    {
      "Sid": "TaggingAccess",
      "Effect": "Allow",
      "Action": [
        "ec2:CreateTags",
        "ec2:DescribeTags"
      ],
      "Resource": "*"
    }
  ]
}
```

### Step 2: Set GitHub Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Create the following secrets:

**`AWS_ROLE_ARN`**
```
arn:aws:iam::123456789012:role/GitHubActionsRole-macro-live-data-viewer
```
(Replace with your account ID and role name)

**`PULUMI_ACCESS_TOKEN`**
1. Log in to [app.pulumi.com](https://app.pulumi.com)
2. **Settings** → **Access Tokens** → **Create token**
3. Copy and paste the full token

**`PULUMI_CONFIG_PASSPHRASE`**
```
your-secure-passphrase-here
```
(Can be any strong string; used to encrypt Pulumi state)

### Step 3: Push to GitHub

```bash
# Ensure you're in the main branch
git checkout main

# Push any changes
git push origin main
```

This will trigger the **Deploy** workflow.

### Step 4: Monitor Deployment

1. Go to **Actions** tab in GitHub
2. Watch the **Deploy** workflow
3. Once complete, check the job output for website URL and S3 bucket information

---

## Verification

### 1. Check S3 Bucket

```bash
aws s3 ls s3://macro-live-data-viewer-dev-bucket/
```

Should see:
```
index.html
data.js
bond_yields_10y.csv
stock_indices.csv
currencies.csv
sentiment_data.csv
sentiment_data_domestic.csv
countries_tickers.csv
```

### 2. Check S3 Bucket Contents (Verification)

```bash
# List bucket contents
aws s3 ls s3://macro-live-data-viewer-dev-bucket/ --recursive

# Get bucket summary
aws s3 ls s3://macro-live-data-viewer-dev-bucket/ --human-readable --summarize
```

### 3. Test Website

```bash
# Get URL
WEBSITE_URL=$(cd infrastructure && pulumi stack output website_url)

# Test with curl
curl -I $WEBSITE_URL

# Should return 200 OK
```

### 4. Browser Test

Open the website URL in a browser. You should see:
- Dashboard loads correctly
- Charts render
- Data displays
- No CORS errors in console

---

## Nightly Data Updates

The **Nightly Data Update** workflow runs automatically at 8 PM UTC every day.

### Manual Trigger

1. Go to **Actions** → **Nightly Data Fetch and Update**
2. Click **Run workflow** → **Run workflow**

### Monitor Updates

1. Check workflow logs in GitHub Actions
2. Verify files in S3:
```bash
aws s3 ls s3://macro-live-data-viewer-dev-bucket/ --human-readable --summarize
```

### Customize Schedule

To change the schedule, edit `.github/workflows/nightly-data-update.yml`:

```yaml
schedule:
  # Cron format: minute hour day month day-of-week
  - cron: "0 20 * * *"  # 8 PM UTC every day
  - cron: "0 */6 * * *" # Every 6 hours
  - cron: "0 9 * * 1"   # 9 AM UTC every Monday
```

---

## Troubleshooting

### Deployment Issues

**Error: Access Denied**
```
Error: error: aws:s3:Bucket (macro-live-data-viewer-dev-bucket): Error putting S3 bucket: ...
```
→ Check AWS credentials, ensure IAM role has S3 permissions

**Error: Pulumi state lock**
```
Error: Acquiring state lock...
```
→ Another deployment is running, wait or use `pulumi cancel`

**Error: Access Denied**
→ Check AWS credentials, ensure IAM role has S3 permissions

### Data Update Issues

**Workflow timeout**
→ Increase timeout in workflow or split into multiple jobs

**API rate limiting**
→ Add delays in fetch scripts, contact API providers

**S3 sync fails**
→ Check AWS credentials in GitHub secrets, ensure bucket exists

### Website Issues

**Blank page or 404 errors**
→ Check S3 bucket contents in AWS Console
→ Clear browser cache:
```bash
aws s3 ls s3://macro-live-data-viewer-dev-bucket/ --human-readable --summarize
```

**CORS errors in browser console**
→ S3 bucket has CORS configuration, check Pulumi code

**Data not loading**
→ Check if `data.js` exists in S3
→ Verify browser can fetch from S3

### Cleanup

**Delete AWS resources:**
```bash
cd infrastructure
pulumi destroy --yes
```

**Delete Pulumi stack:**
```bash
pulumi stack rm dev
```

---

## Additional Resources

- [Pulumi Documentation](https://www.pulumi.com/docs/)
- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [OIDC in GitHub Actions](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)

---

## Support

For issues:
1. Check GitHub Actions logs
2. Review Pulumi deployment history: `pulumi history`
3. Check AWS CloudTrail for API errors
4. Review script logs locally: `python fetch_data.py` (with verbose output if available)
