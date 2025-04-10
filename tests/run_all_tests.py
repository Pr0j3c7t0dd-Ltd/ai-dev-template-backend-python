"""
Run all tests for the FastAPI application.

This script uses pytest to run both functional and E2E tests.
"""

import os
import sys

import pytest


def main():
    """Run all tests for the FastAPI application."""
    print("=" * 46)
    print("Running FastAPI Test Suite with pytest")
    print("=" * 46)

    # Configure test environment
    os.environ["TESTING"] = "true"

    # Run functional tests
    print("\n\n=== Running Python Functional Tests ===")
    functional_result = pytest.main(
        ["-v", "-m", "functional or not e2e", "tests/functional"]
    )

    # Run E2E Playwright tests through pytest
    print("\n\n=== Running E2E API Tests with Playwright ===")
    e2e_result = pytest.main(
        ["-v", "-m", "e2e", "tests/conftest.py::test_playwright_e2e"]
    )

    # Report results
    print("\n\n=== Test Results ===")
    print(f"Functional Tests: {'PASSED' if functional_result == 0 else 'FAILED'}")
    print(f"E2E Tests: {'PASSED' if e2e_result == 0 else 'FAILED'}")

    # Set exit code based on combined results
    if functional_result != 0 or e2e_result != 0:
        print("\n\n=== Some tests failed ===")
        sys.exit(1)
    else:
        print("\n\n=== All tests passed ===")
        sys.exit(0)


if __name__ == "__main__":
    main()
