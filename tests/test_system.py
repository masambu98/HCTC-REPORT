"""
Comprehensive Test Suite for HCTC-CRM
Copyright (c) 2025 - Signature: 8598

Professional test suite covering all system functionality.
"""

import pytest
import json
import time
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

# Add src to path
import sys
from pathlib import Path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.database import Message, init_database, get_db_session
from src.services import get_message_service
from src.api.webhook_app import app
from src.config import config
from src.utils.agents import extract_initials_and_strip
from src.database import AgentSchedule, AgentLeave, get_db_session


class TestDatabase:
    """Test database functionality."""
    
    def setup_method(self):
        """Setup test database."""
        init_database()
        self.message_service = get_message_service()
    
    def test_message_creation(self):
        """Test message creation and retrieval."""
        # Create test message
        message = self.message_service.log_message(
            agent="TestAgent",
            platform="WhatsApp",
            recipient="+1234567890",
            content="Test message",
            message_type="text",
            is_incoming=True
        )
        
        assert message.id is not None
        assert message.agent == "TestAgent"
        assert message.platform == "WhatsApp"
        assert message.recipient == "+1234567890"
        assert message.content == "Test message"
        assert message.is_incoming == True
    
    def test_message_retrieval(self):
        """Test message retrieval with filters."""
        # Create test messages
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Message 1",
            is_incoming=True
        )
        
        self.message_service.log_message(
            agent="Agent2",
            platform="Facebook",
            recipient="+2222222222",
            content="Message 2",
            is_incoming=False
        )
        
        # Test retrieval
        messages = self.message_service.get_messages(limit=10)
        assert len(messages) >= 2
        
        # Test platform filter
        whatsapp_messages = self.message_service.get_messages(platform="WhatsApp")
        assert all(msg.platform == "WhatsApp" for msg in whatsapp_messages)
        
        # Test agent filter
        agent1_messages = self.message_service.get_messages(agent="Agent1")
        assert all(msg.agent == "Agent1" for msg in agent1_messages)
    
    def test_message_statistics(self):
        """Test message statistics generation."""
        # Create test data
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Test message 1",
            is_incoming=True
        )
        
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Test reply 1",
            is_incoming=False
        )
        
        # Get statistics
        stats = self.message_service.get_message_statistics()
        
        assert "total_messages" in stats
        assert "platforms" in stats
        assert "agents" in stats
        assert "direction" in stats
        assert stats["total_messages"] >= 2
        assert "WhatsApp" in stats["platforms"]
        assert "Agent1" in stats["agents"]


class TestWebhookAPI:
    """Test webhook API functionality."""
    
    def setup_method(self):
        """Setup test client."""
        self.client = app.test_client()
        init_database()
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] in ['healthy', 'unhealthy']
        assert 'signature' in data
        assert data['signature'] == '8598'
    
    def test_webhook_verification(self):
        """Test webhook verification."""
        response = self.client.get('/webhook', query_string={
            'hub.mode': 'subscribe',
            'hub.verify_token': config.webhook.verify_token,
            'hub.challenge': 'test_challenge'
        })
        
        assert response.status_code == 200
        assert response.data.decode() == 'test_challenge'

    def test_extract_initials_utility(self):
        """Test initials extraction utility."""
        assert extract_initials_and_strip("^BM Hello") == ("Hello", "BM")
        assert extract_initials_and_strip("Hello ^bm") == ("Hello", "BM")
        assert extract_initials_and_strip("^BM: Hello") == ("Hello", "BM")
        assert extract_initials_and_strip("Hello world") == ("Hello world", None)
    
    def test_webhook_verification_invalid_token(self):
        """Test webhook verification with invalid token."""
        response = self.client.get('/webhook', query_string={
            'hub.mode': 'subscribe',
            'hub.verify_token': 'invalid_token',
            'hub.challenge': 'test_challenge'
        })
        
        assert response.status_code == 401
    
    def test_whatsapp_message_processing(self):
        """Test WhatsApp message processing."""
        payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "123456789",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "+1234567890",
                            "phone_number_id": "987654321"
                        },
                        "messages": [{
                            "from": "+1987654321",
                            "id": "test_message_id",
                            "timestamp": str(int(time.time())),
                            "type": "text",
                            "text": {
                                "body": "Test WhatsApp message"
                            }
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        response = self.client.post('/webhook', 
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['signature'] == '8598'

    def test_send_with_initials_and_excel_report(self):
        """Test /send parsing initials and daily excel report endpoint."""
        # Send an outgoing message with initials token
        payload = {"agent": "Agent1", "to": "+15550001111", "text": "^BM Hello there"}
        resp = self.client.post('/send', data=json.dumps(payload), content_type='application/json')
        assert resp.status_code == 200

        # Request daily excel for Agent1
        resp2 = self.client.get('/reports/agent-daily-excel', query_string={"agent": "Agent1"})
        assert resp2.status_code == 200
        # Should be an Excel MIME type
        assert resp2.headers.get('Content-Type', '').startswith('application/vnd.openxmlformats-officedocument')

    def test_schedule_import_export_and_leave(self):
        """Test schedule import/export and leave creation affects reports."""
        # Import one schedule
        import json
        from datetime import datetime, timedelta
        now = datetime.now().isoformat()
        later = (datetime.now() + timedelta(hours=8)).isoformat()
        payload = {"items": [{"agent": "Agent2", "date": now, "shift_start": now, "shift_end": later, "role": "Agent"}]}
        r = self.client.post('/team/schedules/import', data=json.dumps(payload), content_type='application/json')
        assert r.status_code == 200
        # Export schedules CSV
        start_d = datetime.now().strftime('%Y-%m-%d')
        end_d = start_d
        r2 = self.client.get('/team/schedules/export', query_string={"start": start_d, "end": end_d})
        assert r2.status_code == 200
        assert r2.headers.get('Content-Type', '').startswith('text/csv')
        # Create leave in >7 days should pass
        future_start = (datetime.now() + timedelta(days=8)).isoformat()
        future_end = (datetime.now() + timedelta(days=9)).isoformat()
        leave_body_ok = {"agent": "Agent2", "start_date": future_start, "end_date": future_end, "reason": "Vacation", "status": "approved"}
        r3 = self.client.post('/team/leaves', data=json.dumps(leave_body_ok), content_type='application/json')
        assert r3.status_code == 200
        # Create leave within 7 days should fail
        soon_start = (datetime.now() + timedelta(days=2)).isoformat()
        soon_end = (datetime.now() + timedelta(days=3)).isoformat()
        leave_body_bad = {"agent": "Agent2", "start_date": soon_start, "end_date": soon_end, "reason": "Short notice"}
        r4 = self.client.post('/team/leaves', data=json.dumps(leave_body_bad), content_type='application/json')
        assert r4.status_code == 400

        # Create escalation
        esc = {"agent": "Agent2", "reason": "Customer threatens chargeback", "priority": "high", "recipient": "+15550001111"}
        r5 = self.client.post('/team/escalations', data=json.dumps(esc), content_type='application/json')
        assert r5.status_code == 200
    
    def test_facebook_message_processing(self):
        """Test Facebook message processing."""
        payload = {
            "object": "page",
            "entry": [{
                "id": "123456789",
                "time": int(time.time()),
                "messaging": [{
                    "sender": {"id": "123456789"},
                    "recipient": {"id": "987654321"},
                    "timestamp": int(time.time()),
                    "message": {
                        "mid": "test_message_id",
                        "text": "Test Facebook message"
                    }
                }]
            }]
        }
        
        response = self.client.post('/webhook', 
                                  data=json.dumps(payload),
                                  content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert data['signature'] == '8598'


class TestMessageService:
    """Test message service functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        init_database()
        self.message_service = get_message_service()
    
    def test_agent_performance_tracking(self):
        """Test agent performance tracking."""
        # Create test messages for Agent1
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Incoming message 1",
            is_incoming=True
        )
        
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Reply message 1",
            is_incoming=False
        )
        
        # Create test messages for Agent2
        self.message_service.log_message(
            agent="Agent2",
            platform="Facebook",
            recipient="+2222222222",
            content="Incoming message 2",
            is_incoming=True
        )
        
        # Get agent performance
        agent1_perf = self.message_service.get_agent_performance("Agent1")
        agent2_perf = self.message_service.get_agent_performance("Agent2")
        
        assert agent1_perf['agent'] == "Agent1"
        assert agent1_perf['total_messages'] >= 2
        assert agent1_perf['incoming_messages'] >= 1
        assert agent1_perf['outgoing_messages'] >= 1
        
        assert agent2_perf['agent'] == "Agent2"
        assert agent2_perf['total_messages'] >= 1
        assert agent2_perf['incoming_messages'] >= 1
    
    def test_conversation_thread_tracking(self):
        """Test conversation thread tracking."""
        # Create conversation thread
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Hello, how can I help?",
            is_incoming=True
        )
        
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="I need help with my order",
            is_incoming=True
        )
        
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Sure, what's your order number?",
            is_incoming=False
        )
        
        # Get conversation threads
        threads = self.message_service.get_conversation_threads()
        
        assert len(threads) >= 1
        thread = threads[0]
        assert thread['recipient'] == "+1111111111"
        assert thread['platform'] == "WhatsApp"
        assert thread['agent'] == "Agent1"
        assert thread['message_count'] >= 3
    
    def test_message_search(self):
        """Test message search functionality."""
        # Create test messages
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1111111111",
            content="Order number 12345",
            is_incoming=True
        )
        
        self.message_service.log_message(
            agent="Agent2",
            platform="Facebook",
            recipient="+2222222222",
            content="Refund request",
            is_incoming=True
        )
        
        # Search for order-related messages
        order_messages = self.message_service.search_messages("order")
        assert len(order_messages) >= 1
        assert any("order" in msg.content.lower() for msg in order_messages)
        
        # Search for refund-related messages
        refund_messages = self.message_service.search_messages("refund")
        assert len(refund_messages) >= 1
        assert any("refund" in msg.content.lower() for msg in refund_messages)


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def setup_method(self):
        """Setup test environment."""
        init_database()
        self.client = app.test_client()
        self.message_service = get_message_service()
        # Seed one schedule for Agent1 now
        from datetime import datetime, timedelta, timezone as _tz
        now = datetime.now(_tz.utc)
        with get_db_session() as s:
            s.add(AgentSchedule(agent="Agent1", date=now, shift_start=now - timedelta(hours=1), shift_end=now + timedelta(hours=7), role="Agent"))
    
    def test_complete_whatsapp_workflow(self):
        """Test complete WhatsApp message workflow."""
        # Simulate incoming WhatsApp message
        whatsapp_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "123456789",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "+1234567890",
                            "phone_number_id": "987654321"
                        },
                        "messages": [{
                            "from": "+1987654321",
                            "id": "workflow_test_msg",
                            "timestamp": str(int(time.time())),
                            "type": "text",
                            "text": {
                                "body": "I need help with my order #12345"
                            }
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        # Process webhook
        response = self.client.post('/webhook', 
                                  data=json.dumps(whatsapp_payload),
                                  content_type='application/json')
        assert response.status_code == 200
        
        # Simulate agent reply
        self.message_service.log_message(
            agent="Agent1",
            platform="WhatsApp",
            recipient="+1987654321",
            content="Hi! I can help you with order #12345. What's the issue?",
            is_incoming=False,
            status="sent"
        )
        
        # Verify conversation tracking
        threads = self.message_service.get_conversation_threads()
        assert len(threads) >= 1
        
        # Verify agent performance
        agent_perf = self.message_service.get_agent_performance("Agent1")
        assert agent_perf['total_messages'] >= 1
        assert agent_perf['outgoing_messages'] >= 1

        # Now a new incoming should associate to Agent1 via conversation
        self.message_service.log_message(
            agent=self.message_service.resolve_incoming_agent("+1987654321", "WhatsApp"),
            platform="WhatsApp",
            recipient="+1987654321",
            content="Thanks! The issue is delayed delivery",
            is_incoming=True,
            status="received"
        )

        # Request handled report
        resp = self.client.get('/reports/agent-handled-daily-excel', query_string={"agent": "Agent1"})
        assert resp.status_code == 200
        assert resp.headers.get('Content-Type', '').startswith('application/vnd.openxmlformats-officedocument')

        # Availability endpoint check
        resp2 = self.client.get('/team/schedules/availability', query_string={"agents": "Agent1"})
        assert resp2.status_code == 200
    
    def test_error_handling(self):
        """Test error handling and recovery."""
        # Test invalid webhook payload
        response = self.client.post('/webhook', 
                                  data=json.dumps({"invalid": "payload"}),
                                  content_type='application/json')
        assert response.status_code == 400
        
        # Test empty payload
        response = self.client.post('/webhook', 
                                  data="",
                                  content_type='application/json')
        assert response.status_code == 400
        
        # Test malformed JSON
        response = self.client.post('/webhook', 
                                  data="invalid json",
                                  content_type='application/json')
        assert response.status_code == 400


def run_tests():
    """Run all tests."""
    print("🚀 Running HCTC-CRM Test Suite - Signature: 8598")
    print("=" * 60)
    
    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("=" * 60)
    print("✅ Test Suite Complete - Signature: 8598")


if __name__ == "__main__":
    run_tests()
