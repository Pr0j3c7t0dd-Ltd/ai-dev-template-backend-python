# Modern FastAPI Server

A modern FastAPI server with Swagger documentation, structured following best practices.

## Features

- FastAPI with automatic Swagger/ReDoc documentation
- CORS middleware configured
- Environment-based settings
- API versioning
- Health check endpoint
- Supabase authentication and user management
- Clean project structure

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

For local development, also install development dependencies and set up pre-commit hooks:
```bash
pip install -r requirements-dev.txt
pre-commit install  # Sets up git hooks for automatic code quality checks
```

3. Create a `.env` file in the root directory:
```env
# Environment Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
LOG_TO_FILE=false
LOG_FILE_PATH=logs/app.log

# Supabase Settings (Required)
# Get these from your Supabase project settings (https://app.supabase.com/project/_/settings/api)
SUPABASE_URL=your-project-url                   # Project URL
SUPABASE_KEY=your-anon-key                      # Project API keys -> anon public
SUPABASE_JWT_SECRET=your-jwt-secret             # Project API keys -> JWT secret
```

## Development Setup

The project uses several development tools to maintain code quality:

- **pytest**: For running tests
- **ruff**: For linting and code formatting
- **pre-commit**: For running checks before commits
- **pytest-playwright**: For end-to-end testing

These tools are configured in `requirements-dev.txt` and will be installed when you run `pip install -r requirements-dev.txt`.

## Supabase Setup

### Cloud-hosted Supabase

1. Create a Supabase Project:
   - Go to [Supabase](https://app.supabase.com)
   - Create a new project
   - Note down your project URL and API keys

2. Configure Authentication:
   - In your Supabase project dashboard, go to Authentication -> Settings
   - Configure your desired auth providers (Email, Google, GitHub, etc.)
   - Set up any additional security settings (password strength, etc.)

3. Update Environment Variables:
   - Copy your project's URL and API keys from the Supabase dashboard
   - Update your `.env` file with these values
   - Never commit the `.env` file to version control

### Local Supabase with Docker (Recommended for Development)

For local development, you can run Supabase locally using Docker:

1. Prerequisites:
   - [Docker](https://docs.docker.com/get-docker/) installed and running
   - [Supabase CLI](https://supabase.com/docs/guides/cli) (will be installed by our setup script)

2. Setup Local Supabase:
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh

   # Setup and start local Supabase
   ./scripts/setup_local_supabase.sh
   ```

   This script will:
   - Install Supabase CLI if not already installed
   - Initialize a local Supabase project
   - Start the local Supabase instance
   - Create a `.env.local` file with the correct configuration

3. Managing Local Supabase:
   ```bash
   # Show available commands
   ./scripts/manage_local_supabase.sh

   # Start Supabase
   ./scripts/manage_local_supabase.sh start

   # Stop Supabase
   ./scripts/manage_local_supabase.sh stop

   # Check status
   ./scripts/manage_local_supabase.sh status
   ```

4. Accessing Local Supabase:
   - Studio UI: http://localhost:54323
   - API Endpoint: http://localhost:54321
   - Database: PostgreSQL running on port 54322

5. Using Local Supabase with the Development Server:
   ```bash
   # The development server script will automatically use local Supabase if available
   ./scripts/start_dev_server.sh
   ```

## Running the Server

You can start the development server in two ways:

### Using the development script (recommended)
```bash
./scripts/start_dev_server.sh
```
This script will automatically:
- Create and activate the virtual environment if needed
- Install/update dependencies
- Create a default .env file if it doesn't exist
- Start the development server
- Check for and use local Supabase if available

### Manual start
```bash
python -m src.main
```

The server will be available at:
- API: http://localhost:8000
- Swagger Documentation: http://localhost:8000/docs
- ReDoc Documentation: http://localhost:8000/redoc

## API Endpoints

- `GET /`: Root endpoint - Server status
- `GET /api/v1/health`: Health check endpoint (public)
- `GET /api/v1/me`: Get current user information (requires authentication)
- More endpoints coming soon...

## Testing

This project uses pytest for both functional tests and Playwright for E2E API tests.

### Simple Testing with pytest

You can run tests directly with pytest:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test files
pytest tests/functional/test_health.py

# Run tests matching a specific marker (functional or e2e)
pytest -m functional
```

### Comprehensive Test Runner

For a more structured test experience, use the test runner script:

```bash
python -m tests.run_all_tests
```

This script runs both functional and E2E tests with formatted output.

### Running Only Functional Tests

To run only the functional tests:

```bash
python -m pytest -v -m functional tests/functional
```

### Running Only E2E Tests

To run only the E2E API tests with Playwright:

```bash
python -m pytest -v -m e2e tests/conftest.py::test_playwright_e2e
```

### Running Specific Test Files

To run a specific test file:

```bash
python -m pytest -v tests/functional/test_health.py
```

### Test Environment

Tests use a separate `.env.test` file with mock Supabase credentials to avoid depending on real services:

```env
SUPABASE_URL=https://test-supabase-url.com
SUPABASE_KEY=test-supabase-key
SUPABASE_JWT_SECRET=test-supabase-jwt-secret
```

This file should be created automatically when running tests for the first time. If you're getting Supabase validation errors when running tests, make sure this file exists in the project root.

## Authentication

All API endpoints (except `/api/v1/health`) require authentication using a JWT token from Supabase. To authenticate:

1. Get a JWT token from your Supabase client
2. Include the token in your API requests:
```bash
curl -H "Authorization: Bearer your-jwt-token" http://localhost:8000/api/v1/me
```

## User Settings Feature

The application automatically creates a user settings record for each authenticated user:

- When a user signs up, a trigger automatically creates an entry in the `user_settings` table
- When an existing user logs in, the API middleware checks for and creates a user settings record if one doesn't exist
- Default user settings include:
  - `theme`: "light" (default)
  - `language`: "en" (default)
  - `timezone`: "UTC" (default)

This feature ensures that every authenticated user always has a corresponding settings record, eliminating the need for separate creation steps after registration.

## Running Tests

This project uses pytest for both functional tests and to orchestrate E2E API tests with Playwright.

### Running All Tests

To run all tests (both functional and E2E):

```bash
python -m tests.run_all_tests
```

### Running Only Functional Tests

To run only the functional tests:

```bash
python -m pytest -v -m functional tests/functional
```

### Running Only E2E Tests

To run only the E2E API tests with Playwright:

```bash
python -m pytest -v -m e2e tests/conftest.py::test_playwright_e2e
```

### Running Specific Test Files

To run a specific test file:

```bash
python -m pytest -v tests/functional/test_health.py
```
