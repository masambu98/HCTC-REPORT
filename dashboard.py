"""
HCTC-CRM Dashboard Application
Copyright (c) 2025 - Signature: 8598

Professional analytics dashboard for call center management.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.dashboard.dashboard_app import app
from src.database import init_database
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

def main():
    """Main dashboard entry point."""
    try:
        logger.info("🚀 Starting HCTC-CRM Dashboard - Signature: 8598")
        
        # Initialize database
        init_database()
        logger.info("✅ Database initialized successfully")
        
        # Start the dashboard
        app.run_server(
            host=os.getenv('DASHBOARD_HOST', '0.0.0.0'),
            port=int(os.getenv('DASHBOARD_PORT', 8050)),
            debug=os.getenv('DEBUG', 'False').lower() == 'true'
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start dashboard: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()