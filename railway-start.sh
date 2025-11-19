#!/bin/bash
# Railway startup script
# This runs when Railway starts your service

echo "=========================================="
echo "Starting AI Screener on Railway"
echo "=========================================="

# Check if we're the backend or frontend service
if [ -f "api_server.py" ]; then
    echo "Starting Backend API..."
    python api_server.py
elif [ -f "frontend/package.json" ]; then
    echo "Starting Frontend..."
    cd frontend
    npm start
else
    echo "Error: Could not determine service type"
    exit 1
fi

