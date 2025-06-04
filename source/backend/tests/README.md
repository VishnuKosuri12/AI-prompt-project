# Backend API Testing

## Overview

This directory contains tests for the backend API. As per item #7 in the TESTING.md file, we've rebuilt the testing approach to focus on real database connections rather than mocks.

## Key Changes

1. **Removed Mock-Based Tests**: Deleted the previous mock-based tests (`test_backend.py` and `test_integration.py`) as they were not connecting to the actual database.
2. **Added Database-Connected Tests**: Created new test files that establish real connections to the database.
3. **Ordered Test Execution**: Tests are designed to run in a specific order to manage dependencies between test cases.

## Current Test Files

- `tests_user.py`: Tests for user management endpoints, including:
  - User roles retrieval
  - Listing all users
  - Creating new users
  - Retrieving user info
  - Updating users
  - Deleting users

## Running the Tests

To run the tests, use the updated `run_tests.sh` script:

Make sure you enable the python environment:
    source venv/bin/activate

```bash
# Run all available tests
./run_tests.sh

# Run only user tests
./run_tests.sh user
```

## Test Execution Flow

The tests in `tests_user.py` follow a specific order to ensure proper execution:

1. First, test the roles endpoint to verify available user roles
2. Test listing users to verify existing users
3. Create a test user and verify success
4. Retrieve the test user's information and verify it
5. Update the test user (change role from technician to manager)
6. Delete the test user and verify it's gone

This ensures a complete test of the user management lifecycle.

## Design Principles

- **Real Database Connection**: All tests connect to the actual database rather than using mocks
- **Ordered Execution**: Tests are designed to run in a specific order
- **Self-Contained**: Each test file handles its own setup and teardown
- **Comprehensive Verification**: Tests validate both success scenarios and proper error handling

## Future Additions

Additional test files will be created for other modules following the same approach:
- `tests_chemical.py` for chemical management 
- `tests_location.py` for location management
- `tests_auth.py` for authentication
- `tests_preferences.py` for user preferences

Each will follow the pattern established in `tests_user.py` of testing with real database connections.
