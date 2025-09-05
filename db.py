from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from config import DATABASE_URL
import json

Base = declarative_base()

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    agent = Column(String)       # Agent's name
    platform = Column(String)    # WhatsApp / Facebook
    recipient = Column(String)   # Name or phone number
    content = Column(Text)       # Message text
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    message_type = Column(String)  # text, image, attachment, etc.
    message_id = Column(String)    # Platform message ID
    sender_id = Column(String)     # Sender identifier
    is_incoming = Column(Boolean, default=True)  # True for incoming, False for outgoing
    status = Column(String)        # received, sent, delivered, etc.
    extra_data = Column(Text)      # JSON string for additional platform data

# Database setup
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)


def init_db():
    Base.metadata.create_all(engine)


def log_message(agent, platform, recipient, content, message_type=None, message_id=None,
                sender_id=None, is_incoming=True, status="received", extra_data=None):
    session = Session()

    # Ensure extra_data is stored as JSON text
    if extra_data is not None and not isinstance(extra_data, str):
        try:
            extra_data = json.dumps(extra_data, ensure_ascii=False)
        except Exception:
            # Fallback to string representation if serialization fails
            extra_data = str(extra_data)

    msg = Message(
        agent=agent,
        platform=platform,
        recipient=recipient,
        content=content,
        message_type=message_type,
        message_id=message_id,
        sender_id=sender_id,
        is_incoming=is_incoming,
        status=status,
        extra_data=extra_data
    )

    session.add(msg)
    session.commit()
    session.close()
