#!/bin/bash

# Fix Git Issue and Push Railway Deployment Fixes
echo "🔧 Fixing Git Issue and Pushing Railway Deployment Fixes..."

# Check current directory
echo "📁 Current directory: $(pwd)"

# List all files to see structure
echo "📋 Files in current directory:"
ls -la

# Check if there's a nested ProductivityFlow folder
if [ -d "ProductivityFlow" ]; then
    echo "⚠️  Found nested ProductivityFlow folder, removing it..."
    rm -rf ProductivityFlow
    echo "✅ Nested folder removed"
else
    echo "✅ No nested ProductivityFlow folder found"
fi

# Check git status
echo "🔍 Git status:"
git status

# Add all files
echo "📦 Adding all files to git..."
git add .

# Check status again
echo "🔍 Git status after add:"
git status

# Commit changes
echo "💾 Committing Railway deployment fixes..."
git commit -m "Fix: Railway deployment - simplified for reliability

- Simplified railway.json for Railway deployment
- Removed gunicorn dependency causing deployment failures
- Created simple start.py using Flask's built-in server
- Simplified database initialization and health check
- Updated Procfile for Railway compatibility
- Added comprehensive deployment fixes guide"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Done! Railway deployment fixes should now be pushed to GitHub." 