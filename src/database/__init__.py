"""
Database package for HCTC-CRM
Copyright (c) 2025 - Signature: 8598
"""

from .models import Message, Agent, Conversation, SystemLog, AgentSchedule, AgentLeave, AgentEscalation, Base
from .connection import (
    DatabaseManager, 
    db_manager, 
    get_database_manager, 
    init_database, 
    get_session, 
    get_db_session
)

__all__ = [
    "Message", "Agent", "Conversation", "SystemLog", "AgentSchedule", "AgentLeave", "AgentEscalation", "Base",
    "DatabaseManager", "db_manager", "get_database_manager", 
    "init_database", "get_session", "get_db_session"
]
