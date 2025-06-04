#!/bin/bash

# Script to run unit tests for the search module
# This script should be run from the source/search directory

# Activate virtual environment
source ../../venv/bin/activate

# Ensure we're in the right directory
if [[ $(basename $(pwd)) != "search" ]]; then
  echo "Error: This script must be run from the search module directory (source/search)"
  echo "Current directory: $(pwd)"
  echo "Please change to the source/search directory and try again"
  exit 1
fi

echo "Setting up environment for testing..."

# Install required dependencies from requirements.txt
echo "Installing test dependencies..."
pip install -r tests/requirements.txt

# Create __init__.py file in tests directory if it doesn't exist
if [ ! -f tests/__init__.py ]; then
  echo "Creating tests/__init__.py..."
  touch tests/__init__.py
fi

echo "Running tests for search module..."

# Run pytest with coverage report
pytest tests/test_search.py -v --cov=. --cov-report=term

# Check if tests passed
if [ $? -eq 0 ]; then
  echo -e "\n✅ All tests passed!"
else
  echo -e "\n❌ Some tests failed."
  exit 1
fi
