#!/usr/bin/env python3
"""
Pulumi Infrastructure Setup Helper
Helps initialize and deploy the infrastructure for Macro Live Data Viewer
"""

import subprocess
import sys
import os
import json
from pathlib import Path

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_header(msg):
    print(f"{GREEN}{'='*50}{RESET}")
    print(f"{GREEN}{msg}{RESET}")
    print(f"{GREEN}{'='*50}{RESET}")

def run_command(cmd, check=True):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.returncode

def check_prerequisite(cmd, name):
    """Check if a command is available"""
    output, code = run_command(f"{cmd} --version", check=False)
    if code != 0:
        return False, None
    return True, output.split('\n')[0]

def main():
    print_header("Macro Live Data Viewer - Deploy Setup")
    print()

    # Check prerequisites
    print(f"{YELLOW}Checking prerequisites...{RESET}")

    # Python 3
    has_python, version = check_prerequisite("python3", "Python")
    if has_python:
        print_success(f"Python 3 found: {version}")
    else:
        print_error("Python 3 is not installed")
        sys.exit(1)

    # Pulumi
    has_pulumi, version = check_prerequisite("pulumi", "Pulumi")
    if has_pulumi:
        print_success(f"Pulumi found: {version}")
    else:
        print_error("Pulumi CLI is not installed")
        print("Install with: curl -fsSL https://get.pulumi.com | sh")
        sys.exit(1)

    # AWS CLI
    has_aws, version = check_prerequisite("aws", "AWS CLI")
    if not has_aws:
        print_warning("AWS CLI is not installed, installing...")
        run_command("pip install awscli")
    else:
        print_success(f"AWS CLI found: {version}")

    print()

    # Check AWS credentials
    print(f"{YELLOW}Checking AWS credentials...{RESET}")
    output, code = run_command("aws sts get-caller-identity", check=False)
    if code != 0:
        print_error("AWS credentials not configured")
        print("Run: aws configure")
        sys.exit(1)

    account_data = json.loads(output)
    account_id = account_data.get("Account", "unknown")
    print_success(f"AWS credentials valid (Account: {account_id})")

    print()

    # Navigate to infrastructure directory
    infra_dir = Path(__file__).parent
    os.chdir(infra_dir)

    print(f"{YELLOW}Setting up Pulumi stack...{RESET}")
    print()

    # Ask for stack name
    stack_name = input(f"Enter stack name (default: prod): ").strip() or "prod"

    # Initialize stack
    output, code = run_command(f"pulumi stack select {stack_name}", check=False)
    if code == 0:
        print_success(f"Using existing stack: {stack_name}")
    else:
        print(f"{YELLOW}Creating new stack: {stack_name}{RESET}")
        run_command(f"pulumi stack init {stack_name}")

    print()

    # Ask if they want to preview first
    preview = input(f"Would you like to preview the deployment? (y/n): ").strip().lower()
    if preview == "y":
        print(f"{YELLOW}Running pulumi preview...{RESET}")
        run_command("pulumi preview --diff")
        print()

    # Ask if they want to deploy
    deploy = input(f"Ready to deploy? (y/n): ").strip().lower()
    if deploy != "y":
        print(f"{YELLOW}Deployment cancelled{RESET}")
        sys.exit(0)

    # Deploy
    print(f"{YELLOW}Deploying infrastructure...{RESET}")
    run_command("pulumi up --yes")

    print()
    print_header("Deployment Successful!")
    print()

    # Get outputs
    print(f"{YELLOW}Deployment Information:{RESET}")
    
    output, _ = run_command("pulumi stack output bucket_name")
    print(f"{GREEN}S3 Bucket:{RESET} {output}")
    
    output, _ = run_command("pulumi stack output website_url")
    website_url = output
    print(f"{GREEN}Website URL:{RESET} {website_url}")

    print()
    print(f"{YELLOW}Next steps:{RESET}")
    print(f"1. Test your website: {website_url}")
    print("2. Set up GitHub secrets for CI/CD (see DEPLOYMENT.md)")
    print("3. Push to GitHub to trigger automated deployment")
    print()
    print("For more information, see: DEPLOYMENT.md")

if __name__ == "__main__":
    main()
