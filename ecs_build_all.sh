#!/usr/bin/env python3

import os
import sys
import subprocess
import argparse
import logging
from typing import Optional

# --- Configuration & Setup ---

# Set up logging for informative output
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

APP_NAME = "chemtrack"
SOURCE_DIR = "./source"

# --- Functions ---

def run_command(command: list[str], check: bool = True, log_output: bool = True) -> Optional[str]:
    """
    Executes a shell command and optionally checks for errors.

    Args:
        command: The command as a list of strings (e.g., ['podman', 'build', ...]).
        check: If True, raise an exception on non-zero exit code.
        log_output: If True, log stdout/stderr of the command.

    Returns:
        The command's stdout as a string, or None if it fails and check is False.
    """
    command_str = " ".join(command)
    logging.debug(f"Executing: {command_str}")
    try:
        # Capture output for successful commands to return, but pipe stderr/stdout for real-time logging
        # We redirect stdout/stderr to the parent's file descriptors to log in real-time
        result = subprocess.run(
            command,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        if log_output and result.stdout:
             # Log the output only on success, otherwise it's logged via the exception below
            for line in result.stdout.strip().split('\n'):
                logging.info(f"    | {line}")

        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command_str}")
        logging.error(f"Exit code: {e.returncode}")
        # Log the combined stdout/stderr from the failed command
        if e.output:
            for line in e.output.strip().split('\n'):
                logging.error(f"    | {line}")
        raise
    except FileNotFoundError:
        logging.error(f"Error: Command not found. Is '{command[0]}' installed and in your PATH?")
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while running command: {e}")
        raise


def get_aws_details(aws_region: str) -> tuple[str, str, str]:
    """Retrieves AWS account ID and constructs the ECR registry URI."""
    logging.info("Retrieving AWS account ID...")
    # Use Boto3 for a cleaner way to get the account ID
    try:
        import boto3
        sts_client = boto3.client('sts', region_name=aws_region)
        account_id = sts_client.get_caller_identity()['Account']
        ecr_registry = f"{account_id}.dkr.ecr.{aws_region}.amazonaws.com"
        return account_id, ecr_registry, aws_region
    except ImportError:
        logging.error("The 'boto3' library is not installed. Please install it with 'pip install boto3'.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to get AWS account ID or connect to AWS: {e}")
        sys.exit(1)


def ensure_ecr_repository(image_name: str, aws_region: str):
    """
    Ensures the ECR repository exists, creating it if necessary.
    """
    try:
        import boto3
        ecr_client = boto3.client('ecr', region_name=aws_region)
        logging.info(f"Checking for ECR repository: {image_name}")

        # Try to describe the repository
        try:
            ecr_client.describe_repositories(repositoryNames=[image_name])
            logging.info("Repository exists.")
        except ecr_client.exceptions.RepositoryNotFoundException:
            # If not found, create it
            logging.warning(f"Repository '{image_name}' not found. Creating it...")
            ecr_client.create_repository(
                repositoryName=image_name,
                imageTagMutability='MUTABLE' # Default is MUTABLE, but good to be explicit
            )
            logging.info("Repository created successfully.")

    except Exception as e:
        logging.error(f"Failed to ensure ECR repository existence: {e}")
        raise


def build_and_push(container_name: str, ecr_registry: str, aws_region: str):
    """
    Builds, tags, and pushes a single container image.
    """
    image_name = f"{APP_NAME}/{container_name}"
    ecr_repo_uri = f"{ecr_registry}/{image_name}"
    build_context = os.path.join(SOURCE_DIR, container_name)

    print(f"\n--- Processing: {container_name} ---")

    if not os.path.isdir(build_context):
        logging.error(f"Build context directory not found: {build_context}. Skipping.")
        return

    # 1. Ensure ECR repository exists.
    ensure_ecr_repository(image_name, aws_region)

    # 2. Build the container image.
    logging.info(f"Building image: {image_name}")
    run_command(['podman', 'build', '-t', image_name, build_context])

    # 3. Tag the image for ECR.
    logging.info(f"Tagging image for ECR: {ecr_repo_uri}:latest")
    run_command(['podman', 'tag', image_name, f"{ecr_repo_uri}:latest"])

    # 4. Push the image to ECR.
    logging.info("Pushing image to ECR...")
    run_command(['podman', 'push', f"{ecr_repo_uri}:latest"])

    print(f"✅ Successfully processed container: {container_name}")


def main():
    """Main execution flow of the script."""
    # Use argparse for better command-line argument handling
    parser = argparse.ArgumentParser(
        description="A robust script to build and push container images to Amazon ECR.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'aws_region',
        nargs='?', # Makes the argument optional
        default='us-east-1',
        help="The AWS region to use (e.g., us-west-2). Default: us-east-1"
    )
    args = parser.parse_args()
    aws_region = args.aws_region

    print("=" * 45)
    print("  Building and Pushing Containers to ECR")
    print("=" * 45)

    try:
        # Get AWS details
        account_id, ecr_registry, aws_region = get_aws_details(aws_region)

        print(f"AWS Region:     {aws_region}")
        print(f"AWS Account ID: {account_id}")
        print(f"ECR Registry:   {ecr_registry}")
        print(f"Source Dir:     {SOURCE_DIR}")
        print("-" * 45)

        # Login to ECR
        logging.info("Attempting to log in to ECR...")
        # Get password via AWS CLI and pipe it to podman login
        password = run_command(
            ['aws', 'ecr', 'get-login-password', '--region', aws_region],
            log_output=False
        )
        # Use subprocess.run with input for piping
        subprocess.run(
            ['podman', 'login', '--username', 'AWS', '--password-stdin', ecr_registry],
            input=password,
            text=True,
            check=True,
            capture_output=True # Capture to prevent password being logged
        )
        logging.info("ECR login successful.")

        # Discover and process each container in the source directory
        processed_count = 0
        for container_name in os.listdir(SOURCE_DIR):
            container_path = os.path.join(SOURCE_DIR, container_name)
            if os.path.isdir(container_path):
                build_and_push(container_name, ecr_registry, aws_region)
                processed_count += 1

        if processed_count == 0:
            logging.warning(f"\nNo container directories found in {SOURCE_DIR}. Nothing to do.")
        else:
            print("\n" + "=" * 45)
            print("  All containers built and pushed successfully!")
            print("=" * 45)

    except Exception as e:
        logging.critical(f"\n❌ Script failed due to an error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
