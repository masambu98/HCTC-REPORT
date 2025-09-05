"""
Validation utilities for HCTC-CRM
Copyright (c) 2025 - Signature: 8598
"""

from typing import Dict, Any, List


def validate_whatsapp_payload(data: Dict[str, Any]) -> bool:
    """Validate WhatsApp webhook payload structure."""
    required_fields = ['object', 'entry']
    
    if not all(field in data for field in required_fields):
        return False
    
    if data['object'] != 'whatsapp_business_account':
        return False
    
    if not isinstance(data['entry'], list) or len(data['entry']) == 0:
        return False
    
    entry = data['entry'][0]
    if 'changes' not in entry:
        return False
    
    return True


def validate_facebook_payload(data: Dict[str, Any]) -> bool:
    """Validate Facebook webhook payload structure."""
    required_fields = ['object', 'entry']
    
    if not all(field in data for field in required_fields):
        return False
    
    if data['object'] != 'page':
        return False
    
    if not isinstance(data['entry'], list) or len(data['entry']) == 0:
        return False
    
    return True
