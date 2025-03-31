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
    echo "Error: Supabase CLI is not installed. Please run ./scripts/setup_local_supabase.sh first."
    exit 1
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR/.."

# Navigate to project root
cd "$PROJECT_ROOT"

# Function to display help
function show_help {
    echo "Manage local Supabase instance"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start      Start local Supabase instance"
    echo "  stop       Stop local Supabase instance"
    echo "  restart    Restart local Supabase instance"
    echo "  status     Show status of local Supabase instance"
    echo "  reset      Reset local Supabase database (WARNING: This will delete all data)"
    echo "  help       Show this help message"
    echo ""
}

# No arguments provided
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

# Parse command
case "$1" in
    start)
        echo "Starting local Supabase instance..."
        supabase start
        echo "Local Supabase is running!"
        ;;
    stop)
        echo "Stopping local Supabase instance..."
        supabase stop
        echo "Local Supabase stopped."
        ;;
    restart)
        echo "Restarting local Supabase instance..."
        supabase stop || true
        supabase start
        echo "Local Supabase restarted!"
        ;;
    status)
        echo "Checking local Supabase status..."
        supabase status
        ;;
    reset)
        echo "WARNING: This will delete all data in your local Supabase database."
        read -p "Are you sure you want to continue? (y/N): " confirm
        if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
            echo "Resetting local Supabase database..."
            supabase db reset
            echo "Database reset complete."
        else
            echo "Database reset canceled."
        fi
        ;;
    help)
        show_help
        ;;
    *)
        echo "Error: Unknown command '$1'"
        show_help
        exit 1
        ;;
esac
