#!/usr/bin/env python3
"""
Simplified startup script for Railway deployment
"""
import os
import sys
import logging
from application import application, initialize_database

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function for Railway"""
    try:
        logger.info("Starting ProductivityFlow backend on Railway")
        
        # Initialize database
        logger.info("Initializing database...")
        initialize_database()
        logger.info("Database initialized successfully")
        
        # Get port from Railway environment
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting server on port {port}")
        
        # Start the Flask application
        application.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()