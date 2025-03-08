#!/bin/bash

# Create a build directory
mkdir -p build

# Copy all files from zurich_restaurants to build
cp -r zurich_restaurants/* build/

echo "Build completed. Files copied to build directory." 