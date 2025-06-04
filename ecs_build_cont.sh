#!/bin/bash

# Script to build and push a container to ECR
# Usage: ./build_and_push.sh container nc

# Default region if not provided
AWS_REGION="us-east-1"
ECR_REGISTRY="767397980456.dkr.ecr.${AWS_REGION}.amazonaws.com"
APP_NAME="chemtrack"

CONTAINER_NAME=$1

if [ "$2" = "nc" ]; then
    NO_CACHE_OPTON="--no-cache"
else
    NO_CACHE_OPTON=""
fi


echo "=== Building and pushing containers to ECR ==="
echo "AWS Region: ${AWS_REGION}"
echo "ECR Registry: ${ECR_REGISTRY}"

# Login to ECR
echo "Logging in to ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

# Function to build and push a container
build_and_push() {
    local cname=$1
    local image_tag="${APP_NAME}/${cname}"
    local ecr_repo="${ECR_REGISTRY}/${image_tag}"

    echo "cname ${cname}"
    echo "image tag ${image_tag}"
    echo "ecr_repo ${ecr_repo}"
    
    echo ""
    echo "=== Processing ${cname} container ==="
    
    # Check if repository exists, create if it doesn't
    if ! aws ecr describe-repositories --repository-names ${image_tag} --region ${AWS_REGION} &> /dev/null; then
        echo "Creating ECR repository: ${image_tag}"
        aws ecr create-repository --repository-name ${image_tag} --region ${AWS_REGION}
    fi
    
    # Build the container
    echo "Building container: ${cname}"
    docker build $NO_CACHE_OPTON -t $image_tag ./source/$cname
    
    # Tag the container for ECR
    echo "Tagging container for ECR: ${ecr_repo}"
    docker tag $image_tag $ecr_repo:latest
    
    # Push to ECR
    echo "Pushing container to ECR: ${ecr_repo}"
    docker push $ecr_repo:latest
    
    echo "Container ${cname} successfully built and pushed to ECR"
}

# Build and push each container
build_and_push $CONTAINER_NAME

echo ""
echo "done"
