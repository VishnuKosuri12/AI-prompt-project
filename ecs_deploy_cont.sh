#!/bin/bash

# Script to force deploy a container to ECS using AWS CLI commands

AWS_REGION="us-east-1"
echo $AWS_REGION

APP_NAME="chemtrack"
CLUSTER_NAME="${APP_NAME}-cluster"

if [ "$1" = "shared-templates" ]; then
    SERVICE_NAME="${APP_NAME}-${1}"
else
    SERVICE_NAME="${APP_NAME}-${1}-service"
fi


echo "=== Deploying containers to ECS ==="
echo "AWS Region: ${AWS_REGION}"
echo "Cluster Name: ${CLUSTER_NAME}"
echo "Service Name: ${SERVICE_NAME}"

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI is not installed or not in PATH"
    exit 1
fi

# Check if user is authenticated with AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "Error: Not authenticated with AWS. Please configure AWS CLI credentials."
    exit 1
fi

# Function to update an ECS service
update_service() {
    # Force a new deployment of the service
    echo "Forcing new deployment for service ${service_full_name}..."
    aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment --region $AWS_REGION --output json > /dev/null
}

update_service $1

echo ""
echo "Application URL: https://chemtrack.767397980456.aws.glpoly.net"
