#!/bin/bash

# Exit on error
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "Supabase CLI not found. Installing..."

    # Install Supabase CLI based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install supabase/tap/supabase
    else
        # Linux and others (using NPM)
        npm install -g supabase
    fi
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Navigate to project root
cd "$PROJECT_ROOT"

# Initialize Supabase project if not already initialized
if [ ! -d "supabase" ]; then
    echo "Initializing Supabase project..."
    supabase init
fi

# Start Supabase local development
echo "Starting local Supabase instance..."
supabase start

# Get local Supabase credentials and display them
echo "Local Supabase is running!"
echo "--------------------------------------------------------"
echo "API URL:      $(supabase status | grep API | awk '{print $NF}')"
echo "Database URL: $(supabase status | grep DB | awk '{print $NF}')"
echo "Studio URL:   http://localhost:54323"
echo "Anon Key:     $(supabase status | grep anon | awk '{print $NF}')"
echo "JWT Secret:   $(supabase status | grep JWT | awk '{print $NF}')"
echo "--------------------------------------------------------"
echo "To stop Supabase, run: supabase stop"

# Create/update .env.local with Supabase credentials if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local with local Supabase credentials..."
    cat > .env.local << EOF
# Local Environment Settings
ENVIRONMENT=development
LOG_LEVEL=DEBUG
LOG_TO_FILE=false
LOG_FILE_PATH=logs/app.log

# Local Supabase Settings
SUPABASE_URL=$(supabase status | grep API | awk '{print $NF}')
SUPABASE_ANON_KEY=$(supabase status | grep anon | awk '{print $NF}')
SUPABASE_SERVICE_ROLE_KEY=$(supabase status | grep service_role | awk '{print $NF}')
SUPABASE_JWT_SECRET=$(supabase status | grep JWT | awk '{print $NF}')
EOF

    echo ".env.local file created with local Supabase credentials"
fi

echo "Setup complete! You can now use the local Supabase instance for development."
