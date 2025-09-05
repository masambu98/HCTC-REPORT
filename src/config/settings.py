"""
Configuration Management System
Copyright (c) 2025 - Signature: 8598

Centralized configuration management with environment variable support
and validation for production deployment.
"""

import os
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Application environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str
    echo: bool = False
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class WhatsAppConfig:
    """WhatsApp Business API configuration."""
    access_token: str
    phone_id: str
    business_account_id: str
    api_version: str = "v18.0"
    base_url: str = "https://graph.facebook.com"


@dataclass
class FacebookConfig:
    """Facebook Messenger API configuration."""
    page_access_token: str
    page_id: str
    app_id: str
    app_secret: str
    api_version: str = "v18.0"
    base_url: str = "https://graph.facebook.com"


@dataclass
class WebhookConfig:
    """Webhook configuration settings."""
    verify_token: str
    secret_key: str
    port: int = 5000
    host: str = "0.0.0.0"
    debug: bool = False


@dataclass
class DashboardConfig:
    """Dashboard configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8050
    debug: bool = False
    refresh_interval: int = 10000  # milliseconds


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_bytes: int = 10485760  # 10MB
    backup_count: int = 5


class Config:
    """
    Main configuration class with environment-based settings.
    Signature: 8598
    """
    
    def __init__(self):
        self.environment = Environment(os.getenv("ENVIRONMENT", "development"))
        self.signature = "8598"
        
        # Database configuration
        self.database = DatabaseConfig(
            url=os.getenv("DATABASE_URL", "sqlite:///callcenter.db"),
            echo=self.environment == Environment.DEVELOPMENT
        )
        
        # WhatsApp configuration
        self.whatsapp = WhatsAppConfig(
            access_token=os.getenv("WHATSAPP_ACCESS_TOKEN", ""),
            phone_id=os.getenv("WHATSAPP_PHONE_ID", ""),
            business_account_id=os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
        )
        
        # Facebook configuration
        self.facebook = FacebookConfig(
            page_access_token=os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", ""),
            page_id=os.getenv("FACEBOOK_PAGE_ID", ""),
            app_id=os.getenv("META_APP_ID", ""),
            app_secret=os.getenv("META_APP_SECRET", "")
        )
        
        # Webhook configuration
        self.webhook = WebhookConfig(
            verify_token=os.getenv("WEBHOOK_VERIFY_TOKEN", "callcenter_verify_123"),
            secret_key=os.getenv("FLASK_SECRET_KEY", "your_secret_key_here"),
            port=int(os.getenv("PORT", "5000")),
            host=os.getenv("HOST", "0.0.0.0"),
            debug=self.environment == Environment.DEVELOPMENT
        )
        
        # Dashboard configuration
        self.dashboard = DashboardConfig(
            host=os.getenv("DASHBOARD_HOST", "0.0.0.0"),
            port=int(os.getenv("DASHBOARD_PORT", "8050")),
            debug=self.environment == Environment.DEVELOPMENT
        )
        
        # Logging configuration
        self.logging = LoggingConfig(
            level=os.getenv("LOG_LEVEL", "INFO"),
            file_path=os.getenv("LOG_FILE", None)
        )
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        Returns True if valid, False otherwise.
        """
        required_whatsapp = [
            self.whatsapp.access_token,
            self.whatsapp.phone_id,
            self.whatsapp.business_account_id
        ]
        
        if not all(required_whatsapp):
            print("Warning: WhatsApp configuration incomplete")
            return False
        
        return True
    
    def get_database_url(self) -> str:
        """Get database URL with proper formatting for different environments."""
        if self.environment == Environment.PRODUCTION:
            # For production, ensure proper PostgreSQL URL format
            if not self.database.url.startswith("postgresql://"):
                raise ValueError("Production requires PostgreSQL database")
        
        return self.database.url


# Global configuration instance
config = Config()
