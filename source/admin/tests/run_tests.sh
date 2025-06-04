#!/bin/bash

# Activate virtual environment
source ../../venv/bin/activate

# Install test requirements
echo "Installing test requirements..."
pip install -r tests/requirements.txt

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/test_admin.py -v --cov=. --cov-report=term-missing

# Deactivate virtual environment
deactivate

echo "Testing complete!"
