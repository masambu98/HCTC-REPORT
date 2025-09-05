"""
HCTC-CRM Main Application
Copyright (c) 2025 - Signature: 8598

Professional WhatsApp & Facebook Messenger Integration Platform
Enterprise-grade call center management system.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.api.webhook_app import app
from src.database import init_database
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def main():
    """Main application entry point."""
    try:
        logger.info("🚀 Starting HCTC-CRM Webhook Server - Signature: 8598")
        
        # Initialize database
        init_database()
        logger.info("✅ Database initialized successfully")
        
        # Start the application
        app.run(
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', 5000)),
            debug=os.getenv('DEBUG', 'False').lower() == 'true'
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()