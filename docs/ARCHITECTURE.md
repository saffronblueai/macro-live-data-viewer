# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      GitHub Repository                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Application Code                                          │ │
│  │  • index.html (SPA)                                        │ │
│  │  • data.js (dashboard data)                                │ │
│  │  • fetch_data.py (market data fetcher)                     │ │
│  │  • fetch_sentiment.py (sentiment fetcher)                  │ │
│  │  • *.csv files (data storage)                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Infrastructure as Code (Pulumi)                           │ │
│  │  • infrastructure/__main__.py                              │ │
│  │  • infrastructure/Pulumi.yaml                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  GitHub Actions Workflows                                  │ │
│  │  • .github/workflows/deploy.yml                            │ │
│  │  • .github/workflows/nightly-data-update.yml               │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                    │                               │
                    │ Push to main                  │ Scheduled 8 PM UTC
                    │                               │
                    ▼                               ▼
        ┌────────────────────┐      ┌─────────────────────────────┐
        │ GitHub Actions     │      │ GitHub Actions (Scheduled)  │
        │ Deploy Workflow    │      │ Nightly Update Workflow     │
        │                    │      │                             │
        │ • Checkout code    │      │ • Download from S3          │
        │ • Setup Python     │      │ • Run fetch scripts         │
        │ • AWS secret keys  │      │ • Regenerate data.js        │
        │ • Pulumi up        │      │ • Upload to S3              │
        │ • Sync to S3       │      │ • Commit & push (optional)  │
        └────────────────────┘      └─────────────────────────────┘
                    │                               │
                    │                               │
                    └───────────┬───────────────────┘
                                │
                                ▼
                    ┌─────────────────────────────┐
                    │  AWS IAM (User with Access Keys) │
                    │  GitHubActionsRole          │
                    │  • S3 permissions           │
                    └─────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────────┐
                    │    AWS Services             │
                    │                             │
                    │  ┌───────────────────────┐  │
                    │  │ S3 Bucket             │  │
                    │  │ • Static website      │  │
                    │  │ • CORS enabled        │  │
                    │  │ • Public read policy  │  │
                    │  │                       │  │
                    │  │ Files:                │  │
                    │  │ • index.html          │  │
                    │  │ • data.js             │  │
                    │  │ • *.csv files         │  │
                    │  │                       │  │
                    │  │ Website URL:          │  │
                    │  │ s3-website-region.   │  │
                    │  │ amazonaws.com         │  │
                    │  └───────────────────────┘  │
                    └─────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────────┐
                    │   End Users / Browser       │
                    │                             │
                    │ https://bucket-name.       │
                    │ s3-website-region.         │
                    │ amazonaws.com              │
                    │                             │
                    │ Dashboard loads:            │
                    │ • Data visualizations       │
                    │ • Real-time sentiment       │
                    │ • Market data charts        │
                    └─────────────────────────────┘
```

## Data Flow Diagram

```
External APIs                                      Deployment
    │                                                    │
    ├─ FinanceFlowAPI ─────┐                            │
    │  (Bond yields)        │                            │
    │                       ├─► fetch_data.py ────┐     │
    ├─ Yahoo Finance ──────┤  (bonds, stocks,    │     │
    │  (stocks)             │   currencies)        │     │
    │                       │                      │     │
    ├─ Permutable AI ──────┤                      │     │
    │  (sentiment)          ├─► fetch_sentiment.py ┤    │
    │                       │   (sentiment data)   │     │
    └───────────────────────┘                      │     │
                                                   │     │
                                                   ▼     ▼
                                            ┌──────────────────────┐
                                            │  Local Development  │
                                            │                      │
                                            │ CSV Files:           │
                                            │ • bond_yields_10y   │
                                            │ • stock_indices     │
                                            │ • currencies        │
                                            │ • sentiment_data    │
                                            └──────────────────────┘
                                                   │     ▲
                                                   │     │
                                    Regenerate ◄──┤     │
                                    (generate)    │     │
                                                   │     │
                                                   ▼     │
                                            ┌──────────────────────┐
                                            │   data.js            │
                                            │ (JavaScript export   │
                                            │  of all data)        │
                                            └──────────────────────┘
                                                   │
                                                   │ Git Push
                                                   ▼
                                            ┌──────────────────────┐
                                            │  GitHub Actions      │
                                            │  (Deploy Workflow)   │
                                            └──────────────────────┘
                                                   │
                                                   │
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                                    ▼              ▼              ▼
                        ┌────────────────┐  ┌──────────────┐  ┌──────────────┐
                        │ Upload to S3   │  │ Update       │  │ Update       │
                        │                │  │ Website      │  │ Infrastructure
                        │ • index.html   │  │ Index File   │  │ (if needed)   │
                        │ • data.js      │  │ (if needed)  │  │              │
                        │ • *.csv        │  └──────────────┘  └──────────────┘
                        └────────────────┘
                                │
                                ▼
                        ┌───────────────────┐
                        │ S3 Website        │
                        │ (Served directly) │
                        └───────────────────┘
                                │
                                ▼
                        ┌───────────────────┐
                        │ End User Browser  │
                        │ (Loads index.html)│
                        └───────────────────┘
                                │
                                ├─ Fetch data.js
                                ├─ Fetch data files
                                └─ Render dashboard
```

## Deployment Timeline

```
Developer Push Code to GitHub
    │
    ▼
GitHub Actions Triggered (deploy.yml)
    │
    ├─ Checkout Code [~5 sec]
    ├─ Setup Python [~10 sec]
    ├─ Configure AWS credentials [~5 sec]
    ├─ Pulumi Up [~30-60 sec]
    │  ├─ Create/update S3 bucket
    │  ├─ Upload website files
    │  └─ Configure S3 website hosting
    │
    └─ Complete [~2-3 minutes total]
        │
        ▼
    Website Updated & Live
        │
        ├─ Users see updated index.html immediately
        └─ Data persists in S3
```

## Nightly Update Timeline

```
Scheduled Time: 8 PM UTC Daily
    │
    ▼
GitHub Actions Triggered (nightly-data-update.yml)
    │
    ├─ Checkout Code [~5 sec]
    ├─ Setup Python [~10 sec]
    ├─ Configure AWS credentials [~5 sec]
    │
    ├─ Download from S3 [~10 sec]
    │  └─ Existing CSV files
    │
    ├─ Run fetch_sentiment.py --update-all [~2-5 min]
    │  └─ Download latest sentiment data
    │
    ├─ Run fetch_data.py update [~2-5 min]
    │  └─ Download latest market data
    │
    ├─ Regenerate data.js [~5 sec]
    │
    ├─ Upload to S3 [~10 sec]
    │  └─ Updated CSV and JS files
    │
    ├─ Commit & Push (optional) [~10 sec]
    │
    └─ Complete [~5-15 minutes total]
        │
        ▼
    Dashboard has latest data next morning
```

## Cost Flow (Monthly)

```
AWS Services Used
    │
    ├─ S3 Storage
    │  ├─ 10 MB average
    │  └─ Cost: ~$0.02
    │
    ├─ S3 API Requests
    │  ├─ ~1K requests/day
    │  └─ Cost: ~$0.01
    │
    └─ Total: ~$0.03/month
       └─ Likely Free Tier Eligible!
```

## Technology Stack

```
Frontend
├─ HTML5 (index.html)
├─ JavaScript (vanilla, no frameworks)
├─ Chart.js (visualization library)
└─ CSS3 (responsive design)

Backend/Data
├─ Python 3.11+
├─ requests (API calls)
├─ pandas (data processing)
├─ yfinance (market data)
└─ flask (optional local server)

Infrastructure
├─ AWS S3 (storage & website hosting)
├─ AWS IAM (OIDC authentication)
└─ Pulumi (infrastructure as code)

Deployment
├─ GitHub Actions (CI/CD)
├─ Pulumi CLI (local deployment)
└─ Git (version control)

Data Sources
├─ FinanceFlowAPI (bond yields)
├─ Yahoo Finance (stock indices)
├─ Permutable AI (macro sentiment)
└─ CSV files (data storage)
```

## Security Architecture

```
GitHub Repository
    │
    ├─ Public (code visible)
    │
    ├─ Secrets (encrypted in Actions)
    │  ├─ AWS_ROLE_ARN
    │  └─ PULUMI_CONFIG_PASSPHRASE
    │
    └─ Secret Key Authentication Flow
        │
        ├─ GitHub reads AWS_ACCESS_KEY_ID
        ├─ GitHub reads AWS_SECRET_ACCESS_KEY
        └─ AWS authenticates the request
            │
            ▼
        GitHub Actions
            │
            ├─ Temporary AWS credentials
            ├─ No stored AWS keys
            ├─ Credentials expire (~1 hour)
            │
            ▼
        AWS Services
            │
            ├─ S3 Bucket (public read via website hosting)
            └─ IAM role (scoped permissions)
```

---

**Note**: This architecture is designed for simplicity, scalability, and cost-efficiency. S3 static website hosting is a proven pattern for hosting static web applications with excellent performance and minimal cost.
