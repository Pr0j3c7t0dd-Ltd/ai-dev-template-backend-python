"""
Run integration tests for the FastAPI application.

This script uses pytest to run only integration tests.
"""

import os
import sys

import pytest


def main():
    """Run integration tests for the FastAPI application."""
    print("=" * 50)
    print("Running FastAPI Integration Tests with pytest")
    print("=" * 50)

    # Configure test environment
    os.environ["TESTING"] = "true"
    os.environ["RUN_INTEGRATION_TESTS"] = "true"

    # Run integration tests
    print("\n\n=== Running Integration Tests ===")
    result = pytest.main(["-v", "-m", "integration", "tests/integration"])

    # Report results
    print("\n\n=== Test Results ===")
    if result == 0:
        print("Integration Tests: PASSED")
        print("\n\n=== All tests passed ===")
        sys.exit(0)
    else:
        print("Integration Tests: FAILED")
        print("\n\n=== Some tests failed ===")
        sys.exit(1)


if __name__ == "__main__":
    main()
