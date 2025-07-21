#!/bin/bash

echo "🚀 Deploying ProductivityFlow to Railway..."

# Check if we're in the right directory
if [ ! -f "railway.json" ]; then
    echo "❌ Error: railway.json not found. Make sure you're in the project root."
    exit 1
fi

# Generate environment variables
echo "📋 Generating environment variables..."
python generate_railway_env.py

# Add all files to git
echo "📝 Adding files to git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Fix: Railway deployment configuration - simplified for reliability"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Deployment files pushed to GitHub!"
echo ""
echo "📋 Next steps:"
echo "1. Go to Railway dashboard: https://railway.app"
echo "2. Deploy from GitHub repository"
echo "3. Add PostgreSQL database"
echo "4. Set environment variables from railway_env_vars.txt"
echo "5. Monitor deployment logs" 