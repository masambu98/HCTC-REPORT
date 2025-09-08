"""
Database Models for HCTC-CRM
Copyright (c) 2025 - Signature: 8598

SQLAlchemy models for the call center management system.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, foreign
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import json

Base = declarative_base()


class Message(Base):
    """
    Message model for storing all communication data.
    Signature: 8598
    """
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(100), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    recipient = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    message_type = Column(String(50), nullable=True, index=True)
    message_id = Column(String(100), nullable=True, unique=True, index=True)
    sender_id = Column(String(100), nullable=True, index=True)
    is_incoming = Column(Boolean, default=True, nullable=False, index=True)
    status = Column(String(50), nullable=True, index=True)
    extra_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_agent_timestamp', 'agent', 'timestamp'),
        Index('idx_platform_timestamp', 'platform', 'timestamp'),
        Index('idx_recipient_timestamp', 'recipient', 'timestamp'),
        Index('idx_incoming_timestamp', 'is_incoming', 'timestamp'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'agent': self.agent,
            'platform': self.platform,
            'recipient': self.recipient,
            'content': self.content,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'message_type': self.message_type,
            'message_id': self.message_id,
            'sender_id': self.sender_id,
            'is_incoming': self.is_incoming,
            'status': self.status,
            'extra_data': self.extra_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_extra_data(self) -> Optional[Dict[str, Any]]:
        """Parse extra_data JSON string to dictionary."""
        if self.extra_data:
            try:
                return json.loads(self.extra_data)
            except (json.JSONDecodeError, TypeError):
                return None
        return None

    def set_extra_data(self, data: Dict[str, Any]) -> None:
        """Set extra_data from dictionary."""
        if data:
            self.extra_data = json.dumps(data, ensure_ascii=False)
        else:
            self.extra_data = None

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, agent='{self.agent}', platform='{self.platform}', recipient='{self.recipient}')>"


class Agent(Base):
    """
    Agent model for managing call center agents.
    Signature: 8598
    """
    __tablename__ = 'agents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True, unique=True)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to messages via agent name (no FK). View-only to avoid writes.
    messages = relationship(
        "Message",
        primaryjoin="foreign(Message.agent)==Agent.name",
        viewonly=True,
        lazy="selectin",
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, name='{self.name}', is_active={self.is_active})>"


class Conversation(Base):
    """
    Conversation model for tracking message threads.
    Signature: 8598
    """
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient = Column(String(50), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    agent = Column(String(100), nullable=True, index=True)
    last_message_at = Column(DateTime, nullable=False, index=True)
    message_count = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_recipient_platform', 'recipient', 'platform'),
        Index('idx_agent_active', 'agent', 'is_active'),
        Index('idx_last_message', 'last_message_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'recipient': self.recipient,
            'platform': self.platform,
            'agent': self.agent,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'message_count': self.message_count,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, recipient='{self.recipient}', platform='{self.platform}', agent='{self.agent}')>"


class SystemLog(Base):
    """
    System log model for tracking application events.
    Signature: 8598
    """
    __tablename__ = 'system_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True, index=True)
    function = Column(String(100), nullable=True)
    line_number = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    extra_data = Column(Text, nullable=True)

    # Indexes for better query performance
    __table_args__ = (
        Index('idx_level_timestamp', 'level', 'timestamp'),
        Index('idx_module_timestamp', 'module', 'timestamp'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'level': self.level,
            'message': self.message,
            'module': self.module,
            'function': self.function,
            'line_number': self.line_number,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'extra_data': self.extra_data
        }

    def __repr__(self) -> str:
        return f"<SystemLog(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"


class AgentSchedule(Base):
    """
    Agent work schedule model.
    Signature: 8598
    """
    __tablename__ = 'agent_schedules'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    shift_start = Column(DateTime, nullable=False)
    shift_end = Column(DateTime, nullable=False)
    role = Column(String(50), nullable=True)  # e.g., "Agent", "TeamLead"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index('idx_schedule_agent_date', 'agent', 'date'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'agent': self.agent,
            'date': self.date.isoformat() if self.date else None,
            'shift_start': self.shift_start.isoformat() if self.shift_start else None,
            'shift_end': self.shift_end.isoformat() if self.shift_end else None,
            'role': self.role,
            'notes': self.notes,
        }


class AgentLeave(Base):
    """
    Agent leave management model.
    Signature: 8598
    """
    __tablename__ = 'agent_leaves'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent = Column(String(100), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False, index=True)
    end_date = Column(DateTime, nullable=False, index=True)
    reason = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default='approved', index=True)  # requested/approved/denied
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        Index('idx_leave_agent_start_end', 'agent', 'start_date', 'end_date'),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'agent': self.agent,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'reason': self.reason,
            'status': self.status,
        }
