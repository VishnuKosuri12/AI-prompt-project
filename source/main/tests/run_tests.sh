#!/bin/bash

# Parse command line arguments
SKIP_HEALTH_CHECK=false
KEEP_RUNNING=false
SPECIFIC_TEST=""

for arg in "$@"; do
  case $arg in
    --skip-health-check)
      SKIP_HEALTH_CHECK=true
      shift
      ;;
    --keep-running)
      KEEP_RUNNING=true
      shift
      ;;
    -t=*|--test=*)
      SPECIFIC_TEST="${arg#*=}"
      shift
      ;;
    *)
      # Unknown option
      ;;
  esac
done

# Navigate to the script directory
cd "$(dirname "$0")"

echo "Installing test requirements..."
pip install -r requirements.txt --quiet

# Create __init__.py file if it doesn't exist
if [ ! -f __init__.py ]; then
  echo "Creating __init__.py..."
  touch __init__.py
fi

# Start the Docker Compose environment for testing
echo "Starting Docker Compose environment..."
cd ../../../
docker-compose up -d backend login main nginx shared-templates

if [ "$SKIP_HEALTH_CHECK" = false ]; then
  # Function to check if service is healthy
  check_service_health() {
      local service=$1
      local url=$2
      local max_attempts=20
      local wait_seconds=2 # Reduced wait time for faster testing
      local attempt=1
      
      echo "Checking health of $service at $url..."
      
      while [ $attempt -le $max_attempts ]; do
          echo -n "."  # Just print a dot for less verbose output
          if curl -s -f "$url" > /dev/null 2>&1; then
              echo " $service is healthy!"
              return 0
          fi
          
          sleep $wait_seconds
          attempt=$((attempt + 1))
      done
      
      echo "ERROR: $service health check failed after $max_attempts attempts!"
      return 1
  }

  # Use parallel health checks when possible
  echo "Checking service health..."
  if ! check_service_health "backend" "http://localhost:8000/health"; then
      echo "Failed to start backend service, stopping test execution."
      [ "$KEEP_RUNNING" = false ] && docker-compose down
      exit 1
  fi

  if ! check_service_health "login" "http://localhost:8001/health"; then
      echo "Failed to start login service, stopping test execution."
      [ "$KEEP_RUNNING" = false ] && docker-compose down
      exit 1
  fi

  if ! check_service_health "main" "http://localhost:8003/health"; then
      echo "Failed to start main service, stopping test execution."
      [ "$KEEP_RUNNING" = false ] && docker-compose down
      exit 1
  fi

  if ! check_service_health "shared-templates" "http://localhost:8005/health"; then
      echo "Failed to start shared-templates service, stopping test execution."
      [ "$KEEP_RUNNING" = false ] && docker-compose down
      exit 1
  fi

  echo "All services are running and healthy!"
else
  echo "Skipping health checks as requested."
  # Add a small sleep to ensure services have started
  sleep 3
fi

# Run the main tests
echo "Running main integration tests..."
cd source/main/tests

if [ -n "$SPECIFIC_TEST" ]; then
  echo "Running specific test: $SPECIFIC_TEST"
  PYTHONPATH=../.. pytest -v test_main.py::TestMainIntegration::$SPECIFIC_TEST
else
  PYTHONPATH=../.. pytest -v test_main.py
fi

# Get the test result status
TEST_RESULT=$?

# Shut down the Docker Compose environment
if [ "$KEEP_RUNNING" = false ]; then
  echo "Shutting down Docker Compose environment..."
  cd ../../../
  docker-compose down
else
  echo "Keeping Docker Compose environment running as requested."
fi

# Show usage help
echo ""
echo "Usage tips:"
echo "  --skip-health-check: Skip health checks to start tests faster"
echo "  --keep-running: Keep Docker containers running after tests complete"
echo "  --test=test_name: Run only a specific test (e.g. --test=test_display_main_page)"
echo ""
echo "Example: ./run_tests.sh --skip-health-check --keep-running --test=test_user_manager"
echo ""

# Return the test result status
exit $TEST_RESULT
