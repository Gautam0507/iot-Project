#!/bin/bash

echo "Building frontend..."

# Navigate to the frontend directory
cd frontend

# Make sure Node modules are installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build the Svelte app
echo "Running build command..."
npm run build

echo "Frontend build complete!"

# Check if the build was successful
if [ -d "dist" ]; then
    echo "Build successful. Files are in frontend/dist"
else
    echo "Build failed!"
    exit 1
fi

exit 0

