"""
Security utilities for HCTC-CRM
Copyright (c) 2025 - Signature: 8598
"""

import hmac
import hashlib
import re
from typing import Optional
from flask import request


def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Validate webhook signature for security."""
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    text = text.strip()
    
    # Limit length
    return text[:1000] if len(text) > 1000 else text


def is_valid_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return bool(re.match(pattern, phone))


def is_valid_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
