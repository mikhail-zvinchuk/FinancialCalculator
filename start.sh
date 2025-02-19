#!/bin/bash

# Function to check if a command was successful
check_error() {
    if [ $? -ne 0 ]; then
        echo "Error: $1"
        exit 1
    fi
}

# Function to start the Flask backend
start_flask_backend() {
    echo "Starting Flask backend..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        echo "Creating virtual environment..."
        python -m venv .venv
        check_error "Failed to create virtual environment"
    fi
    
    # Activate virtual environment
    source .venv/bin/activate
    check_error "Failed to activate virtual environment"
    
    # Set Flask environment variables
    export FLASK_APP=app.py
    export FLASK_DEBUG=1
    
    # Start Flask in the background
    echo "Starting Flask server..."
    flask run &
    
    # Store the PID of the Flask process
    FLASK_PID=$!
    echo "Flask server started with PID: $FLASK_PID"
}

# Function to start the Vue frontend
start_vue_frontend() {
    echo "Starting Vue frontend..."
    
    cd ui || { echo "Failed to change to ui directory"; exit 1; }
    
    # Start the development server in the background
    echo "Starting Vue development server..."
    npm run dev &
    
    # Store the PID of the npm process
    NPM_PID=$!
    echo "Vue development server started with PID: $NPM_PID"
    
    cd ..
}

# Function to handle script termination
cleanup() {
    echo "Stopping services..."
    # Kill the background processes
    kill $FLASK_PID 2>/dev/null
    kill $NPM_PID 2>/dev/null
    exit 0
}

# Set up trap to handle script termination
trap cleanup SIGINT SIGTERM

# Main execution
echo "Starting Financial Calculator application..."

# Start backend
start_flask_backend

# Give the backend a moment to start
sleep 2

# Start frontend
start_vue_frontend

echo "Both services have been started. You can access the application at http://localhost:5173"
echo "Press Ctrl+C to stop all services."

# Wait for user interrupt
wait 