#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

echo "Installing test requirements..."
pip install -r requirements.txt

# Start the Docker Compose environment for testing
echo "Starting Docker Compose environment..."
cd ../../../
docker-compose up -d backend login main nginx

# Function to check if service is healthy
check_service_health() {
    local service=$1
    local url=$2
    local max_attempts=20
    local wait_seconds=5
    local attempt=1
    
    echo "Checking health of $service at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt of $max_attempts..."
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "$service is healthy!"
            return 0
        fi
        
        echo "$service not ready yet. Waiting $wait_seconds seconds..."
        sleep $wait_seconds
        attempt=$((attempt + 1))
    done
    
    echo "ERROR: $service health check failed after $max_attempts attempts!"
    return 1
}

# Wait for services to be ready
echo "Waiting for backend service to be healthy..."
if ! check_service_health "backend" "http://localhost:8000/health"; then
    echo "Failed to start backend service, stopping test execution."
    docker-compose down
    exit 1
fi

echo "Waiting for login service to be healthy..."
if ! check_service_health "login" "http://localhost:8001/health"; then
    echo "Failed to start login service, stopping test execution."
    docker-compose down
    exit 1
fi

echo "Waiting for main service to be healthy..."
if ! check_service_health "main" "http://localhost:8003/health"; then
    echo "Failed to start main service, stopping test execution."
    docker-compose down
    exit 1
fi

echo "All services are running and healthy!"

# Run the login tests
echo "Running login integration tests..."
cd source/login/tests
#PYTHONPATH=../.. pytest -v test_login.py --disable-warnings
PYTHONPATH=../.. pytest -v test_login.py

# Get the test result status
TEST_RESULT=$?

# Shut down the Docker Compose environment
echo "Shutting down Docker Compose environment..."
cd ../../../
docker-compose down

# Return the test result status
exit $TEST_RESULT
