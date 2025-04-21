#!/bin/bash

# Email Assistant run script
# This script launches the Email Assistant application

# Change to the project root directory
cd "$(dirname "$0")/.."

# Activate virtual environment if available
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Run the application
echo "Starting Email Assistant..."
python -m src.main "$@"