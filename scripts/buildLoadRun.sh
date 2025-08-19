#!/usr/bin/env bash
set -e  # Exit on any error
# Immediately exit if REPO_ROOT is not set
if [ -z "$REPO_ROOT" ]; then
    echo "Error: REPO_ROOT is not set. Run this script from the Nix devShell."
    exit 1
fi
cd $REPO_ROOT

# Simple script to build, load, and run Docker image with Nix
# 1. Build → 2. Load → 3. Run (with auto-cleanup)

echo "🚀 Building Docker image with Nix..."
nix build .#docker

echo "📥 Loading image into Docker..."
IMAGE_TAG=$(docker load < result | grep -o 'monotes-container:[^ ]*')

echo "🏃 Running container on port 7999 (auto-cleanup enabled)..."
docker run --rm -p 7999:7999 "$IMAGE_TAG"
