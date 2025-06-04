#!/bin/bash

# Script to build and push containers to ECR
# Usage: ./build_and_push.sh [aws-region]

# Default region if not provided
AWS_REGION=${1:-"us-east-1"}
ECR_REGISTRY="767397980456.dkr.ecr.${AWS_REGION}.amazonaws.com"
APP_NAME="chemtrack"

echo "=== Building and pushing containers to ECR ==="
echo "AWS Region: ${AWS_REGION}"
echo "ECR Registry: ${ECR_REGISTRY}"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | podman login --username AWS --password-stdin ${ECR_REGISTRY}

# Function to build and push a container
build_and_push() {
    local container_name=$1
    local image_tag="${APP_NAME}/${container_name}"
    local ecr_repo="${ECR_REGISTRY}/${image_tag}"
    
    echo ""
    echo "=== Processing ${container_name} container ==="
    
    # Check if repository exists, create if it doesn't
    if ! aws ecr describe-repositories --repository-names ${image_tag} --region ${AWS_REGION} &> /dev/null; then
        echo "Creating ECR repository: ${image_tag}"
        aws ecr create-repository --repository-name ${image_tag} --region ${AWS_REGION}
    fi
    
    # Build the container
    echo "Building container: ${container_name}"
    podman build -t ${image_tag} ./source/${container_name}
    
    # Tag the container for ECR
    echo "Tagging container for ECR: ${ecr_repo}"
    podman tag ${image_tag} ${ecr_repo}:latest
    
    # Push to ECR
    echo "Pushing container to ECR: ${ecr_repo}"
    podman push ${ecr_repo}:latest
    
    echo "Container ${container_name} successfully built and pushed to ECR"
}

# Build and push each container
build_and_push "backend"
build_and_push "login"
build_and_push "main"
build_and_push "nginx"
build_and_push "search"
build_and_push "shared-templates"
build_and_push "admin"
build_and_push "recipes"
build_and_push "reports"
build_and_push "secrets"

echo ""
echo "=== All containers have been built and pushed to ECR ==="
