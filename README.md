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
pre-commit install
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

## Authentication

All API endpoints (except `/api/v1/health`) require authentication using a JWT token from Supabase. To authenticate:

1. Get a JWT token from your Supabase client
2. Include the token in your API requests:
```bash
curl -H "Authorization: Bearer your-jwt-token" http://localhost:8000/api/v1/me
```