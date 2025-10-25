#!/usr/bin/env python3
"""Build and push container images to Amazon ECR for the ChemTrack application."""

import os
import sys
import subprocess
import argparse
import logging
from typing import Optional, Tuple

# --- Logging configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

APP_NAME = "chemtrack"
SOURCE_DIR = "./source"


def run_command(
    command: list[str],
    *,
    check: bool = True,
    log_output: bool = True
) -> Optional[str]:
    """
    Execute a shell command and optionally check for errors.

    Args:
        command: The command as a list of strings (e.g., ['podman', 'build', ...]).
        check: If True, raise CalledProcessError on non-zero exit code.
        log_output: If True, log the stdout (and stderr if merged) line by line.

    Returns:
        The full stdout output (trimmed) if successful, or None if check=False and it failed.
    """
    command_str = " ".join(command)
    logging.debug(f"Executing: {command_str}")
    try:
        result = subprocess.run(
            command,
            check=check,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        output = result.stdout.strip() if result.stdout else ""
        if log_output and output:
            for line in output.splitlines():
                logging.info(f"    | {line}")
        return output
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {command_str}")
        logging.error(f"Exit code: {e.returncode}")
        if e.output:
            for line in e.output.strip().splitlines():
                logging.error(f"    | {line}")
        raise
    except FileNotFoundError:
        logging.error(
            f"Error: Command not found. Ensure '{command[0]}' is installed and on your PATH."
        )
        raise
    except Exception as e:
        logging.error(f"Unexpected error while running command: {e}")
        raise


def get_aws_details(aws_region: str) -> Tuple[str, str, str]:
    """
    Retrieve AWS account ID and construct the ECR registry URI.

    Args:
        aws_region: The AWS region to use (e.g., "us-east-1").

    Returns:
        A tuple of (account_id, ecr_registry, aws_region).

    Exits the script if the boto3 library is missing or the AWS call fails.
    """
    logging.info("Retrieving AWS account ID...")
    try:
        import boto3
        sts_client = boto3.client('sts', region_name=aws_region)
        account_id = sts_client.get_caller_identity()['Account']
        ecr_registry = f"{account_id}.dkr.ecr.{aws_region}.amazonaws.com"
        return account_id, ecr_registry, aws_region
    except ImportError:
        logging.error("'boto3' library not found. Please install it via 'pip install boto3'.")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to retrieve AWS account or connect to AWS: {e}")
        sys.exit(1)


def ensure_ecr_repository(image_name: str, aws_region: str) -> None:
    """
    Ensure that the ECR repository exists, creating it if necessary.

    Args:
        image_name: Name of the image repository (e.g., "chemtrack/service").
        aws_region: AWS region where ECR resides.
    """
    try:
        import boto3
        ecr = boto3.client('ecr', region_name=aws_region)
        logging.info(f"Checking for ECR repository: {image_name}")
        try:
            ecr.describe_repositories(repositoryNames=[image_name])
            logging.info("Repository already exists.")
        except ecr.exceptions.RepositoryNotFoundException:
            logging.warning(f"Repository '{image_name}' not found — creating it.")
            ecr.create_repository(
                repositoryName=image_name,
                imageTagMutability='MUTABLE'
            )
            logging.info("Repository created successfully.")
    except Exception as e:
        logging.error(f"Failed to ensure ECR repository existence: {e}")
        raise


def build_and_push(container_name: str, ecr_registry: str, aws_region: str) -> None:
    """
    Build, tag, and push a container image to Amazon ECR.

    Args:
        container_name: Directory name under SOURCE_DIR containing the Docker context.
        ecr_registry: The base ECR registry URI (account-specific).
        aws_region: AWS region for the ECR registry.
    """
    image_name = f"{APP_NAME}/{container_name}"
    ecr_repo_uri = f"{ecr_registry}/{image_name}"
    build_context = os.path.join(SOURCE_DIR, container_name)

    print(f"\n--- Processing: {container_name} ---")

    if not os.path.isdir(build_context):
        logging.error(f"Build context not found: {build_context}. Skipping.")
        return

    # 1. Ensure the repository exists in ECR.
    ensure_ecr_repository(image_name, aws_region)

    # 2. Build the container image.
    logging.info(f"Building image: {image_name}")
    run_command(['podman', 'build', '-t', image_name, build_context])

    # 3. Tag the image for ECR.
    tagged = f"{ecr_repo_uri}:latest"
    logging.info(f"Tagging image for ECR: {tagged}")
    run_command(['podman', 'tag', image_name, tagged])

    # 4. Push the image to ECR.
    logging.info("Pushing image to ECR...")
    run_command(['podman', 'push', tagged])

    print(f"✅ Successfully processed container: {container_name}")


def main() -> None:
    """
    Parse arguments and run the build/push pipeline.
    """
    parser = argparse.ArgumentParser(
        description="Build and push container images to Amazon ECR.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'aws_region',
        nargs='?',
        default='us-east-1',
        help="AWS region (default: us-east-1)"
    )
    args = parser.parse_args()
    aws_region = args.aws_region

    print("=" * 45)
    print("  Building and Pushing Containers to ECR")
    print("=" * 45)

    try:
        account_id, ecr_registry, aws_region = get_aws_details(aws_region)

        print(f"AWS Region:     {aws_region}")
        print(f"AWS Account ID: {account_id}")
        print(f"ECR Registry:   {ecr_registry}")
        print(f"Source Dir:     {SOURCE_DIR}")
        print("-" * 45)

        logging.info("Logging in to ECR...")
        password = run_command(
            ['aws', 'ecr', 'get-login-password', '--region', aws_region],
            log_output=False
        )
        subprocess.run(
            ['podman', 'login', '--username', 'AWS', '--password-stdin', ecr_registry],
            input=password,
            text=True,
            check=True,
            capture_output=True
        )
        logging.info("ECR login successful.")

        processed = 0
        for item in os.listdir(SOURCE_DIR):
            path = os.path.join(SOURCE_DIR, item)
            if os.path.isdir(path):
                build_and_push(item, ecr_registry, aws_region)
                processed += 1

        if processed == 0:
            logging.warning(f"No container directories found in '{SOURCE_DIR}'. Nothing to do.")
        else:
            print("\n" + "=" * 45)
            print("  All containers built and pushed successfully!")
            print("=" * 45)

    except Exception as exc:
        logging.critical(f"\n❌ Script failed due to error: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
