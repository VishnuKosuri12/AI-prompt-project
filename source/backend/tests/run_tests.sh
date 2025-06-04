#!/bin/bash

# Navigate to the script directory
cd "$(dirname "$0")"

echo "Installing test requirements..."
pip install -r requirements.txt

# Run user tests
run_user_tests() {
    echo "Running backend API user tests..."
    PYTHONPATH=../.. pytest -v tests_user.py --disable-warnings
}

# Run location tests
run_location_tests() {
    echo "Running backend API location tests..."
    PYTHONPATH=../.. pytest -v tests_location.py --disable-warnings
}

# Run chemical tests
run_chemical_tests() {
    echo "Running backend API chemical tests..."
    PYTHONPATH=../.. pytest -v tests_chemical.py --disable-warnings
}

if [ -z "$1" ]; then
    echo "Running all backend API tests..."
    run_user_tests
    run_location_tests
    run_chemical_tests
else
    if [ "$1" == "user" ]; then
        run_user_tests
    elif [ "$1" == "location" ]; then
        run_location_tests
    elif [ "$1" == "chemical" ]; then
        run_chemical_tests
    else
        echo "Invalid test type: $1"
        echo "Available test types: user, location, chemical"
        exit 1
    fi
fi

# Note: Old mock-based tests (test_backend.py and test_integration.py) have been 
# removed as per task #7 requirements. Tests now connect directly to the database.
