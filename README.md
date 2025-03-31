# Modern FastAPI Server

A modern FastAPI server with Swagger documentation, structured following best practices.

## Features

- FastAPI with automatic Swagger/ReDoc documentation
- CORS middleware configured
- Environment-based settings
- API versioning
- Health check endpoint
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

3. Create a `.env` file in the root directory (optional):
```env
ENVIRONMENT=development
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
- `GET /api/v1/health`: Health check endpoint
- More endpoints coming soon...