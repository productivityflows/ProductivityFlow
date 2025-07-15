#!/bin/bash

echo "🚀 Generating new developer test codes..."
echo ""

cd backend

# Check if requests library is available
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installing required dependencies..."
    sudo apt update && sudo apt install -y python3-requests
fi

# Run the setup script
python3 setup_dev_data.py

# Copy the generated file to root
if [ -f "DEVELOPER_CODES.md" ]; then
    cp DEVELOPER_CODES.md ../DEVELOPER_CODES.md
    echo ""
    echo "✅ Developer codes file copied to root directory"
    echo "📋 View the codes: cat DEVELOPER_CODES.md"
    echo "🔗 Backend URL: https://productivityflow-backend-v3.onrender.com"
else
    echo "❌ Failed to generate developer codes file"
fi