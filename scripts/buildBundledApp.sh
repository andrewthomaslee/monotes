#!/usr/bin/env bash
set -e  # Exit on any error

# Script to build and start the bundledApp
# 1. Build → 2. Run

echo "🚀 Building bundled app..."
nix build

echo "🏃 Running bundled app..."
./result/main.py
