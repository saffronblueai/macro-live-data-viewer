"""
Pulumi infrastructure for Macro Live Data Viewer Dashboard
Deploys a static website to AWS S3 with public read access
"""

import json
import pulumi
import pulumi_aws as aws

# Configuration
config = pulumi.Config()
aws_region = config.get("aws:region") or "us-east-1"

# ============================================================================
# S3 Bucket for Static Website Hosting
# ============================================================================

# Create the S3 bucket for static website
website_bucket = aws.s3.Bucket(
    "macro-live-data-viewer-bucket",
    acl="public-read",
    website=aws.s3.BucketWebsiteArgs(
        index_document="index.html",
        error_document="index.html",  # Route all errors to index for SPA support
    ),
)

# ============================================================================
# S3 Bucket Policy to Allow Public Read Access
# ============================================================================

bucket_policy = aws.s3.BucketPolicy(
    "macro-live-data-viewer-policy",
    bucket=website_bucket.id,
    policy=website_bucket.arn.apply(
        lambda arn: json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"{arn}/*",
                    }
                ],
            }
        )
    ),
)

# ============================================================================
# Outputs
# ============================================================================

pulumi.export("bucket_name", website_bucket.id)
pulumi.export("bucket_regional_domain_name", website_bucket.bucket_regional_domain_name)
pulumi.export("website_url", website_bucket.website_endpoint)
