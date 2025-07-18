#!/usr/bin/env python3
"""
Production startup script for Flask application.
This script ensures proper database initialization without using deprecated before_first_request.
"""

import os
import sys
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the application
try:
    from application import application, init_db, initialize_database
    print("✅ Application imported successfully")
except ImportError as e:
    print(f"❌ Failed to import application: {e}")
    sys.exit(1)

def main():
    """Main startup function for production deployment."""
    print("🚀 Starting Flask application in production mode...")
    
    # Initialize database using the modern approach
    try:
        print("📊 Initializing database...")
        # Use the robust initialize_database function instead of before_first_request
        if initialize_database():
            print("✅ Database initialization successful!")
        else:
            print("❌ Database initialization failed!")
            # Don't exit - let the app try to run anyway
    except Exception as e:
        print(f"⚠️  Database initialization error: {e}")
        # Fallback to simple init_db
        try:
            init_db()
            print("✅ Fallback database initialization successful!")
        except Exception as e2:
            print(f"❌ Fallback database initialization also failed: {e2}")
    
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    print(f"🌐 Starting server on {host}:{port}")
    application.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()