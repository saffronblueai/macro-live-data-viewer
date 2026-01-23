"""
Pulumi infrastructure for Macro Live Data Viewer Dashboard
Deploys a static website to AWS S3 with public read access
"""

import json
import pulumi
import pulumi_aws as aws

# ============================================================================
# S3 Bucket for Static Website Hosting
# ============================================================================

# Create the S3 bucket for static website
website_bucket = aws.s3.Bucket("macro-live-data-viewer-bucket",
    bucket="macro-live-data-viewer-bucket",
    website=aws.s3.BucketWebsiteArgs(
        index_document="index.html",
        error_document="index.html",  # Route all errors to index for SPA support
    ),
)

# ============================================================================
# S3 Public Access Block Configuration
# ============================================================================
# IMPORTANT: Create this BEFORE the bucket policy so BlockPublicPolicy=False
# is in place when we try to apply the public policy

public_access_block = aws.s3.BucketPublicAccessBlock(
    "macro-live-data-viewer-public-access",
    bucket=website_bucket.id,
    block_public_acls=False,
    block_public_policy=False,
    ignore_public_acls=False,
    restrict_public_buckets=False,
)

# ============================================================================
# S3 Bucket Policy to Allow Public Read Access
# ============================================================================
# Now safe to apply the public policy since BlockPublicPolicy=False

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
    opts=pulumi.ResourceOptions(depends_on=[public_access_block]),
)

# ============================================================================
# Outputs
# ============================================================================

pulumi.export("bucket_name", website_bucket.id)
pulumi.export("bucket_regional_domain_name", website_bucket.bucket_regional_domain_name)
pulumi.export("website_url", website_bucket.website_endpoint)
