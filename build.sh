#!/bin/bash

# Navigate to the ui folder and run bun build
cd ui || { echo "Failed to change directory to ui"; exit 1; }

bun install

bun run build

# Check if bun build was successful
if [ $? -ne 0 ]; then
    echo "bun build failed"
    exit 1
fi

# Navigate back to the original directory
cd ..

# Run poetry install in the current folder
poetry install

# Check if poetry install was successful
if [ $? -ne 0 ]; then
    echo "poetry install failed"
    exit 1
fi

echo "Build and installation completed successfully."
