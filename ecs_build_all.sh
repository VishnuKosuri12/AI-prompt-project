#!/bin/bash

# A robust script to build and push container images to Amazon ECR.
#
# This script automatically discovers subdirectories in ./source, treats each
# as a container, builds it, and pushes it to a corresponding ECR repository.
#
# Usage: ./build_and_push.sh [aws-region]
# Example: ./build_and_push.sh us-west-2

# --- Configuration ---
# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error.
set -u
# Fail a pipeline if any command in it fails.
set -o pipefail

# --- Constants ---
# Use a default region if one is not provided as the first argument.
readonly AWS_REGION="${1:-"us-east-1"}"
readonly AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
readonly ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
readonly APP_NAME="chemtrack"
readonly SOURCE_DIR="./source"

# --- Color Codes for Output ---
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[0;33m'
readonly NC='\033[0m' # No Color

# --- Functions ---

# Builds, tags, and pushes a single container image.
# Globals: APP_NAME, ECR_REGISTRY, AWS_REGION, YELLOW, GREEN, NC
# Arguments: $1: The name of the container (subdirectory name).
build_and_push() {
    local container_name=$1
    local image_name="${APP_NAME}/${container_name}"
    local ecr_repo_uri="${ECR_REGISTRY}/${image_name}"
    local build_context="${SOURCE_DIR}/${container_name}"

    echo -e "\n${YELLOW}--- Processing: ${container_name} ---${NC}"

    # 1. Ensure ECR repository exists.
    if ! aws ecr describe-repositories --repository-names "${image_name}" --region "${AWS_REGION}" &>/dev/null; then
        echo "Repository '${image_name}' not found. Creating it..."
        aws ecr create-repository --repository-name "${image_name}" --region "${AWS_REGION}" >/dev/null
        echo "Repository created successfully."
    fi

    # 2. Build the container image.
    echo "Building image: ${image_name}"
    podman build -t "${image_name}" "${build_context}"

    # 3. Tag the image for ECR.
    echo "Tagging image for ECR: ${ecr_repo_uri}:latest"
    podman tag "${image_name}" "${ecr_repo_uri}:latest"

    # 4. Push the image to ECR.
    echo "Pushing image to ECR..."
    podman push "${ecr_repo_uri}:latest"

    echo -e "${GREEN}✔ Successfully processed container: ${container_name}${NC}"
}

# --- Main Execution ---
main() {
    echo "============================================="
    echo "  Building and Pushing Containers to ECR"
    echo "============================================="
    echo "AWS Region:   ${AWS_REGION}"
    echo "ECR Registry: ${ECR_REGISTRY}"
    echo "Source Dir:   ${SOURCE_DIR}"
    echo "---------------------------------------------"

    # Login to ECR
    echo "Attempting to log in to ECR..."
    aws ecr get-login-password --region "${AWS_REGION}" | podman login --username AWS --password-stdin "${ECR_REGISTRY}"
    echo -e "${GREEN}ECR login successful.${NC}"

    # Discover and process each container in the source directory
    for container_path in "${SOURCE_DIR}"/*; do
        if [ -d "${container_path}" ]; then
            container_name=$(basename "${container_path}")
            build_and_push "${container_name}"
        fi
    done

    echo -e "\n${GREEN}============================================="
    echo "  All containers built and pushed successfully!"
    echo "=============================================${NC}"
}

# Run the main function
main "$@"
