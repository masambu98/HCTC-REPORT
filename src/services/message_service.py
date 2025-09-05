"""
Message Service for HCTC-CRM
Copyright (c) 2025 - Signature: 8598

Professional message management service with advanced analytics,
caching, and performance optimization.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
import logging
import json

from ..database import Message, Agent, Conversation, get_db_session
from ..config import config

logger = logging.getLogger(__name__)


class MessageService:
    """
    Professional message management service.
    Signature: 8598
    """
    
    def __init__(self):
        self.signature = "8598"
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def log_message(
        self,
        agent: str,
        platform: str,
        recipient: str,
        content: str,
        message_type: Optional[str] = None,
        message_id: Optional[str] = None,
        sender_id: Optional[str] = None,
        is_incoming: bool = True,
        status: str = "received",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Log a message with comprehensive error handling and validation.
        
        Args:
            agent: Agent name
            platform: Platform (WhatsApp, Facebook, etc.)
            recipient: Recipient identifier
            content: Message content
            message_type: Type of message (text, image, etc.)
            message_id: Platform message ID
            sender_id: Sender identifier
            is_incoming: Whether message is incoming
            status: Message status
            extra_data: Additional platform-specific data
            
        Returns:
            Message: Created message object
            
        Raises:
            ValueError: If required parameters are invalid
            DatabaseError: If database operation fails
        """
        try:
            # Validate required parameters
            if not agent or not platform or not recipient or not content:
                raise ValueError("Agent, platform, recipient, and content are required")
            
            # Sanitize and validate data
            agent = str(agent).strip()[:100]
            platform = str(platform).strip()[:50]
            recipient = str(recipient).strip()[:50]
            content = str(content).strip()
            
            if not content:
                raise ValueError("Message content cannot be empty")
            
            with get_db_session() as session:
                # Create message object
                message = Message(
                    agent=agent,
                    platform=platform,
                    recipient=recipient,
                    content=content,
                    message_type=message_type,
                    message_id=message_id,
                    sender_id=sender_id,
                    is_incoming=is_incoming,
                    status=status,
                    extra_data=json.dumps(extra_data, ensure_ascii=False) if extra_data else None
                )
                
                # Add to session and commit
                session.add(message)
                session.commit()
                session.refresh(message)
                
                # Update conversation tracking
                self._update_conversation(session, message)
                
                self.logger.info(f"Message logged successfully - ID: {message.id}, Agent: {agent}, Platform: {platform}")
                return message
                
        except Exception as e:
            self.logger.error(f"Failed to log message: {e}")
            raise
    
    def _update_conversation(self, session: Session, message: Message) -> None:
        """Update conversation tracking."""
        try:
            # Find or create conversation
            conversation = session.query(Conversation).filter(
                and_(
                    Conversation.recipient == message.recipient,
                    Conversation.platform == message.platform
                )
            ).first()
            
            if conversation:
                # Update existing conversation
                conversation.agent = message.agent
                conversation.last_message_at = message.timestamp
                conversation.message_count += 1
                conversation.updated_at = datetime.now(timezone.utc)
            else:
                # Create new conversation
                conversation = Conversation(
                    recipient=message.recipient,
                    platform=message.platform,
                    agent=message.agent,
                    last_message_at=message.timestamp,
                    message_count=1
                )
                session.add(conversation)
            
            session.commit()
            
        except Exception as e:
            self.logger.error(f"Failed to update conversation: {e}")
            # Don't raise - conversation update is not critical
    
    def get_messages(
        self,
        agent: Optional[str] = None,
        platform: Optional[str] = None,
        recipient: Optional[str] = None,
        is_incoming: Optional[bool] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Message]:
        """
        Get messages with advanced filtering and pagination.
        
        Args:
            agent: Filter by agent name
            platform: Filter by platform
            recipient: Filter by recipient
            is_incoming: Filter by message direction
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            List[Message]: List of message objects
        """
        try:
            with get_db_session() as session:
                query = session.query(Message)
                
                # Apply filters
                if agent:
                    query = query.filter(Message.agent == agent)
                if platform:
                    query = query.filter(Message.platform == platform)
                if recipient:
                    query = query.filter(Message.recipient == recipient)
                if is_incoming is not None:
                    query = query.filter(Message.is_incoming == is_incoming)
                if start_date:
                    query = query.filter(Message.timestamp >= start_date)
                if end_date:
                    query = query.filter(Message.timestamp <= end_date)
                
                # Apply ordering, limit, and offset
                query = query.order_by(desc(Message.timestamp)).limit(limit).offset(offset)
                
                return query.all()
                
        except Exception as e:
            self.logger.error(f"Failed to get messages: {e}")
            raise
    
    def get_message_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive message statistics.
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dict[str, Any]: Statistics dictionary
        """
        try:
            with get_db_session() as session:
                query = session.query(Message)
                
                # Apply date filters
                if start_date:
                    query = query.filter(Message.timestamp >= start_date)
                if end_date:
                    query = query.filter(Message.timestamp <= end_date)
                
                # Total messages
                total_messages = query.count()
                
                # Messages by platform
                platform_stats = query.with_entities(
                    Message.platform, func.count(Message.id)
                ).group_by(Message.platform).all()
                
                # Messages by agent
                agent_stats = query.with_entities(
                    Message.agent, func.count(Message.id)
                ).group_by(Message.agent).all()
                
                # Incoming vs outgoing
                direction_stats = query.with_entities(
                    Message.is_incoming, func.count(Message.id)
                ).group_by(Message.is_incoming).all()
                
                # Messages by hour (for activity patterns)
                hourly_stats = query.with_entities(
                    func.extract('hour', Message.timestamp).label('hour'),
                    func.count(Message.id)
                ).group_by('hour').order_by('hour').all()
                
                # Top recipients
                top_recipients = query.with_entities(
                    Message.recipient, func.count(Message.id).label('count')
                ).group_by(Message.recipient).order_by(desc('count')).limit(10).all()
                
                return {
                    "total_messages": total_messages,
                    "platforms": dict(platform_stats),
                    "agents": dict(agent_stats),
                    "direction": dict(direction_stats),
                    "hourly_activity": dict(hourly_stats),
                    "top_recipients": [{"recipient": r[0], "count": r[1]} for r in top_recipients],
                    "signature": self.signature
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get message statistics: {e}")
            raise
    
    def get_agent_performance(
        self,
        agent: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get agent performance metrics.
        
        Args:
            agent: Agent name
            start_date: Start date for metrics
            end_date: End date for metrics
            
        Returns:
            Dict[str, Any]: Agent performance metrics
        """
        try:
            with get_db_session() as session:
                query = session.query(Message).filter(Message.agent == agent)
                
                # Apply date filters
                if start_date:
                    query = query.filter(Message.timestamp >= start_date)
                if end_date:
                    query = query.filter(Message.timestamp <= end_date)
                
                # Total messages
                total_messages = query.count()
                
                # Incoming vs outgoing
                incoming = query.filter(Message.is_incoming == True).count()
                outgoing = query.filter(Message.is_incoming == False).count()
                
                # Messages by platform
                platform_stats = query.with_entities(
                    Message.platform, func.count(Message.id)
                ).group_by(Message.platform).all()
                
                # Unique recipients
                unique_recipients = query.with_entities(
                    Message.recipient
                ).distinct().count()
                
                # Average response time (simplified)
                response_times = []
                # This would require more complex logic to calculate actual response times
                
                return {
                    "agent": agent,
                    "total_messages": total_messages,
                    "incoming_messages": incoming,
                    "outgoing_messages": outgoing,
                    "platforms": dict(platform_stats),
                    "unique_recipients": unique_recipients,
                    "signature": self.signature
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get agent performance: {e}")
            raise
    
    def get_conversation_threads(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get conversation threads with message counts.
        
        Args:
            limit: Maximum number of threads to return
            offset: Number of threads to skip
            
        Returns:
            List[Dict[str, Any]]: List of conversation thread data
        """
        try:
            with get_db_session() as session:
                conversations = session.query(Conversation).filter(
                    Conversation.is_active == True
                ).order_by(desc(Conversation.last_message_at)).limit(limit).offset(offset).all()
                
                return [conv.to_dict() for conv in conversations]
                
        except Exception as e:
            self.logger.error(f"Failed to get conversation threads: {e}")
            raise
    
    def search_messages(
        self,
        search_term: str,
        agent: Optional[str] = None,
        platform: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """
        Search messages by content, recipient, or agent.
        
        Args:
            search_term: Search term
            agent: Filter by agent
            platform: Filter by platform
            limit: Maximum number of results
            
        Returns:
            List[Message]: List of matching messages
        """
        try:
            with get_db_session() as session:
                query = session.query(Message).filter(
                    or_(
                        Message.content.ilike(f"%{search_term}%"),
                        Message.recipient.ilike(f"%{search_term}%"),
                        Message.agent.ilike(f"%{search_term}%")
                    )
                )
                
                if agent:
                    query = query.filter(Message.agent == agent)
                if platform:
                    query = query.filter(Message.platform == platform)
                
                return query.order_by(desc(Message.timestamp)).limit(limit).all()
                
        except Exception as e:
            self.logger.error(f"Failed to search messages: {e}")
            raise


# Global message service instance
message_service = MessageService()


def get_message_service() -> MessageService:
    """Get the global message service instance."""
    return message_service
