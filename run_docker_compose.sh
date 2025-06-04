#!/bin/bash

# Script to run the ChemTrack application using Docker Compose
# Usage: ./run_docker_compose.sh

# Check if AWS credentials are set
if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
    echo "Warning: AWS credentials are not set in the environment"
    echo "The backend service may not be able to connect to AWS services"
    echo ""
    echo "To set AWS credentials, you can use the following commands:"
    echo "export AWS_ACCESS_KEY_ID=your_access_key"
    echo "export AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "export AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials"
    echo ""
    echo "Or you can add these credentials to a .env file in the same directory as docker-compose.yml:"
    echo "AWS_ACCESS_KEY_ID=your_access_key"
    echo "AWS_SECRET_ACCESS_KEY=your_secret_key"
    echo "AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials"
    echo ""
    
    read -p "Do you want to continue without AWS credentials? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

# Set AWS region if not already set
if [[ -z "${AWS_REGION}" ]]; then
    export AWS_REGION="us-east-1"
    echo "Setting default AWS region to us-east-1"
fi

echo "=== Starting ChemTrack application using Docker Compose ==="

# Stop any existing containers
echo "Stopping any existing containers..."
docker compose down

# Start the containers
echo "Starting containers..."
docker compose up -d

# Check if containers are running
echo ""
echo "=== Checking container status ==="
docker compose ps

echo ""
echo "=== Application is now running locally ==="
echo ""
echo "To view logs, run:"
echo "docker compose logs -f"
echo ""
echo "To stop the application, run:"
echo "docker compose down"
