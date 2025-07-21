#!/usr/bin/env python3
"""
Railway-optimized startup script for Flask application.
Simplified for reliable deployment.
"""

import os
import sys
import logging

# Railway-specific setup
os.environ.setdefault('FLASK_ENV', 'production')

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the application
try:
    from application import application, init_db
    logger.info("✅ Application imported successfully")
except ImportError as e:
    logger.error(f"❌ Failed to import application: {e}")
    sys.exit(1)

def main():
    """Main startup function for Railway deployment."""
    logger.info("🚀 Starting Flask application on Railway...")
    
    # Simple database initialization
    try:
        logger.info("📊 Initializing database...")
        init_db()
        logger.info("✅ Database initialization successful!")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Continue anyway - database might already exist
    
    # Start the application
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    application.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()