#!/usr/bin/env python3
"""
HCTC-CRM System Startup Script
Copyright (c) 2025 - Signature: 8598

Professional startup script for the complete HCTC-CRM system.
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.database import init_database
from src.utils.logging import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

class HCTCCRMSystem:
    """
    HCTC-CRM System Manager
    Signature: 8598
    """
    
    def __init__(self):
        self.processes = {}
        self.running = False
        self.signature = "8598"
    
    def initialize_system(self):
        """Initialize the system components."""
        try:
            logger.info("🚀 Initializing HCTC-CRM System - Signature: 8598")
            
            # Initialize database
            logger.info("📊 Initializing database...")
            init_database()
            logger.info("✅ Database initialized successfully")
            
            # Validate configuration
            logger.info("⚙️ Validating configuration...")
            from src.config import config
            if not config.validate():
                logger.warning("⚠️ Configuration validation failed - some features may not work")
            else:
                logger.info("✅ Configuration validated successfully")
            
            logger.info("🎉 System initialization complete - Signature: 8598")
            return True
            
        except Exception as e:
            logger.error(f"❌ System initialization failed: {e}")
            return False
    
    def start_webhook_service(self):
        """Start the webhook service."""
        try:
            logger.info("🌐 Starting webhook service...")
            
            # Start webhook service
            webhook_process = subprocess.Popen([
                sys.executable, "app.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['webhook'] = webhook_process
            logger.info("✅ Webhook service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start webhook service: {e}")
            return False
    
    def start_dashboard_service(self):
        """Start the dashboard service."""
        try:
            logger.info("📊 Starting dashboard service...")
            
            # Start dashboard service
            dashboard_process = subprocess.Popen([
                sys.executable, "dashboard.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            self.processes['dashboard'] = dashboard_process
            logger.info("✅ Dashboard service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start dashboard service: {e}")
            return False
    
    def start_system(self):
        """Start the complete system."""
        try:
            logger.info("🚀 Starting HCTC-CRM Complete System - Signature: 8598")
            
            # Initialize system
            if not self.initialize_system():
                return False
            
            # Start webhook service
            if not self.start_webhook_service():
                return False
            
            # Wait a moment for webhook to start
            time.sleep(2)
            
            # Start dashboard service
            if not self.start_dashboard_service():
                return False
            
            self.running = True
            logger.info("🎉 HCTC-CRM System started successfully!")
            logger.info("📱 Webhook Service: http://localhost:5000")
            logger.info("📊 Dashboard: http://localhost:8050")
            logger.info("🔗 Health Check: http://localhost:5000/health")
            logger.info("")
            logger.info("Press Ctrl+C to stop the system")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start system: {e}")
            return False
    
    def stop_system(self):
        """Stop the complete system."""
        try:
            logger.info("🛑 Stopping HCTC-CRM System...")
            
            self.running = False
            
            # Stop all processes
            for name, process in self.processes.items():
                if process and process.poll() is None:
                    logger.info(f"🛑 Stopping {name} service...")
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=10)
                        logger.info(f"✅ {name} service stopped")
                    except subprocess.TimeoutExpired:
                        logger.warning(f"⚠️ {name} service didn't stop gracefully, forcing...")
                        process.kill()
                        process.wait()
                        logger.info(f"✅ {name} service force stopped")
            
            logger.info("✅ HCTC-CRM System stopped successfully - Signature: 8598")
            
        except Exception as e:
            logger.error(f"❌ Error stopping system: {e}")
    
    def monitor_system(self):
        """Monitor system health."""
        while self.running:
            try:
                # Check process health
                for name, process in self.processes.items():
                    if process and process.poll() is not None:
                        logger.error(f"❌ {name} service has stopped unexpectedly")
                        self.running = False
                        break
                
                time.sleep(5)  # Check every 5 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Error monitoring system: {e}")
                break
    
    def run(self):
        """Run the complete system."""
        try:
            # Start system
            if not self.start_system():
                logger.error("❌ Failed to start system")
                return False
            
            # Monitor system
            self.monitor_system()
            
            return True
            
        except KeyboardInterrupt:
            logger.info("🛑 Received interrupt signal")
            return True
        except Exception as e:
            logger.error(f"❌ System error: {e}")
            return False
        finally:
            self.stop_system()


def signal_handler(signum, frame):
    """Handle system signals."""
    logger.info("🛑 Received signal, shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run system
    system = HCTCCRMSystem()
    
    try:
        success = system.run()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
