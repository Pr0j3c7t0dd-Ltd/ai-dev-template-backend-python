#!/bin/bash

clear

# Exit on error
set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Navigate to project root
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install/update dependencies
echo "Installing/updating dependencies..."
pip install -r requirements.txt

# Check if .env.local file exists, use it for local development
if [ -f ".env.local" ]; then
    echo "Using local environment configuration (.env.local)..."
    export $(grep -v '^#' .env.local | xargs)
# Otherwise check if .env file exists, create if it doesn't
elif [ ! -f ".env" ]; then
    echo "Creating default .env file..."
    echo "ENVIRONMENT=development" > .env
    echo "Note: For local Supabase development, run ./scripts/setup_local_supabase.sh"
fi

# Check if local Supabase is running and configured
if command -v supabase &> /dev/null; then
    # Check if Supabase is running
    if supabase status 2>/dev/null | grep -q "Database online:"; then
        echo "Local Supabase is running and will be used for development"
    else
        echo "Local Supabase is installed but not running."
        echo "Starting local Supabase..."
        supabase start
    fi
else
    echo "Supabase CLI not found. To develop with local Supabase, run ./scripts/setup_local_supabase.sh"
fi

# Start the development server
echo "Starting development server..."
python -m src.main
