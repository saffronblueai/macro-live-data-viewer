# Pre-Deployment Checklist

Complete this checklist before deploying to production.

## Prerequisites

- [ ] AWS Account created and active
- [ ] GitHub repository created and ready
- [ ] Python 3.11+ installed locally
- [ ] Pulumi CLI installed (`curl -fsSL https://get.pulumi.com | sh`)
- [ ] AWS CLI installed (`pip install awscli`)
- [ ] AWS credentials configured (`aws configure`)

## GitHub Repository Setup

- [ ] Code pushed to GitHub
- [ ] Branch strategy decided (main for prod, develop for staging)
- [ ] Repository is public or GitHub Actions has sufficient permissions
- [ ] README and documentation reviewed

## AWS Account Setup

- [ ] AWS account ID noted: `________________`
- [ ] IAM user created with programmatic access (if not using OIDC)
- [ ] OIDC provider configured (recommended)
- [ ] IAM role created: `GitHubActionsRole-macro-live-data-viewer`
- [ ] IAM policies attached (S3, IAM)
- [ ] Service limits checked (S3 buckets)

## Pulumi Setup

- [ ] Pulumi account created (optional but recommended)
- [ ] Pulumi access token generated: `________________`
- [ ] Local machine can run Pulumi: `pulumi version`
- [ ] Infrastructure code reviewed (`infrastructure/__main__.py`)
- [ ] Cost estimation done (expected ~$0.03-0.50/month)

## GitHub Secrets Configuration

Create these secrets in GitHub (Settings → Secrets):

- [ ] `AWS_ROLE_ARN`
  - Format: `arn:aws:iam::123456789012:role/GitHubActionsRole-macro-live-data-viewer`
  - Value: `________________`

- [ ] `PULUMI_CONFIG_PASSPHRASE`
  - Any secure string for state encryption
  - Value: `[redacted]`

## Local Testing

- [ ] Run `python infrastructure/deploy.py` successfully
- [ ] Infrastructure deployed to AWS
- [ ] Website accessible at S3 URL
- [ ] S3 bucket contains correct files
- [ ] Dashboard loads and displays data
- [ ] Browser console has no errors

## File Verification

- [ ] `infrastructure/__main__.py` - Pulumi infrastructure
- [ ] `infrastructure/Pulumi.yaml` - Project config
- [ ] `infrastructure/Pulumi.dev.yaml` - Stack config
- [ ] `infrastructure/requirements.txt` - Dependencies
- [ ] `.github/workflows/deploy.yml` - CICD deployment
- [ ] `.github/workflows/nightly-data-update.yml` - Data sync
- [ ] `.gitignore` - Git ignore rules
- [ ] `DEPLOYMENT.md` - Full deployment guide
- [ ] `QUICKSTART.md` - Quick reference
- [ ] `SETUP_SUMMARY.md` - Project summary

## Data Files

- [ ] `bond_yields_10y.csv` - Present
- [ ] `stock_indices.csv` - Present
- [ ] `currencies.csv` - Present
- [ ] `sentiment_data.csv` - Present
- [ ] `sentiment_data_domestic.csv` - Present
- [ ] `countries_tickers.csv` - Present
- [ ] `data.js` - Generated and present

## Workflow Testing

- [ ] Push code to main branch
- [ ] Watch GitHub Actions deploy workflow
- [ ] Verify deployment completes successfully
- [ ] Test website functionality after deployment
- [ ] Monitor for any errors in logs

## Nightly Update Testing

- [ ] Manually trigger `nightly-data-update.yml` workflow
- [ ] Verify sentiment data update runs
- [ ] Verify market data update runs
- [ ] Verify data.js regenerated
- [ ] Check S3 files updated with new data
- [ ] Monitor for any errors

## Production Readiness

- [ ] All tests passing
- [ ] No sensitive data in code or commits
- [ ] AWS costs within budget
- [ ] Monitoring set up (CloudWatch, S3)
- [ ] Backup strategy considered
- [ ] Rollback procedure documented

## Monitoring Setup

- [ ] S3 bucket size monitored
- [ ] CloudWatch alarms configured (optional)
- [ ] GitHub Actions notifications enabled
- [ ] Slack/email alerts configured (optional)

## Documentation

- [ ] README.md reviewed and complete
- [ ] DEPLOYMENT.md reviewed for accuracy
- [ ] QUICKSTART.md available for reference
- [ ] Team knows how to:
  - [ ] Trigger manual deployments
  - [ ] Update data files
  - [ ] Monitor deployments
  - [ ] Troubleshoot issues
  - [ ] Access logs

## Final Verification

- [ ] Website loads at production URL
- [ ] Dashboard displays all data correctly
- [ ] Charts render without errors
- [ ] Data updates working (manual test)
- [ ] Browser console clean (no errors/warnings)
- [ ] Mobile responsiveness tested
- [ ] S3 website hosting configured
- [ ] Performance acceptable (check S3 sync logs)

## Production Deployment

- [ ] All checklist items completed
- [ ] Team briefed on deployment
- [ ] Communication channels ready
- [ ] Ready for public access

---

## Post-Deployment

- [ ] Monitor first 24 hours for issues
- [ ] Verify nightly update runs successfully
- [ ] Check metrics for unusual activity
- [ ] Share S3 website URL with stakeholders
- [ ] Document any issues/learnings
- [ ] Update team on deployment status

## Troubleshooting Reference

If issues occur, check:
1. GitHub Actions logs (Actions tab)
2. Pulumi deployment history (`pulumi history`)
3. AWS CloudTrail for API errors
4. S3 request logs
5. S3 bucket contents
6. DEPLOYMENT.md troubleshooting section

---

## Sign-Off

- [ ] Deployed by: `________________` Date: `__________`
- [ ] Reviewed by: `________________` Date: `__________`
- [ ] Approved by: `________________` Date: `__________`

---

**Last Updated**: January 22, 2026  
**Project**: Macro Live Data Viewer  
**Environment**: AWS Production
