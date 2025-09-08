"""
Professional Webhook Application for HCTC-CRM
Copyright (c) 2025 - Signature: 8598

Enterprise-grade webhook handler for WhatsApp Business API and Facebook Messenger
with comprehensive error handling, logging, and security features.
"""

from flask import Flask, request, jsonify, abort, send_file
from werkzeug.exceptions import BadRequest, Unauthorized, InternalServerError
import logging
import json
import hashlib
import hmac
import time
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ..config import config
from ..services import get_message_service
from ..utils.logging import setup_logging
from ..utils.security import validate_webhook_signature, sanitize_input
from ..utils.security import is_valid_phone_number
from ..utils.validators import validate_whatsapp_payload, validate_facebook_payload
from ..utils import extract_initials_and_strip

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Create Flask application
app = Flask(__name__)
app.secret_key = config.webhook.secret_key

# Disable Flask's default logging to use our custom logger
import logging as flask_logging
flask_logging.getLogger('werkzeug').setLevel(flask_logging.WARNING)


class WebhookHandler:
    """
    Professional webhook handler with comprehensive error handling.
    Signature: 8598
    """
    
    def __init__(self):
        self.message_service = get_message_service()
        self.signature = "8598"
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def handle_verification(self, verify_token: str, challenge: str) -> str:
        """
        Handle webhook verification request.
        
        Args:
            verify_token: Token from webhook request
            challenge: Challenge string from webhook request
            
        Returns:
            str: Challenge string if verification successful
            
        Raises:
            Unauthorized: If verification fails
        """
        try:
            self.logger.info(f"Webhook verification attempt - Token: {verify_token}, Challenge: {challenge}")
            
            if verify_token == config.webhook.verify_token:
                self.logger.info("Webhook verification successful - Signature: 8598")
                return challenge
            else:
                self.logger.warning("Webhook verification failed - Invalid token")
                raise Unauthorized("Verification failed")
                
        except Exception as e:
            self.logger.error(f"Webhook verification error: {e}")
            raise Unauthorized("Verification failed")
    
    def handle_whatsapp_message(self, data: Dict[str, Any]) -> None:
        """
        Handle incoming WhatsApp message.
        
        Args:
            data: WhatsApp webhook payload
            
        Raises:
            BadRequest: If payload is invalid
        """
        try:
            # Validate payload structure
            if not validate_whatsapp_payload(data):
                raise BadRequest("Invalid WhatsApp payload structure")
            
            entry = data["entry"][0]
            changes = entry["changes"]
            
            for change in changes:
                if change["value"].get("messages"):
                    for message in change["value"]["messages"]:
                        self._process_whatsapp_message(message, change["value"])
                        
        except Exception as e:
            self.logger.error(f"Error processing WhatsApp message: {e}")
            raise
    
    def handle_facebook_message(self, data: Dict[str, Any]) -> None:
        """
        Handle incoming Facebook Messenger message.
        
        Args:
            data: Facebook webhook payload
            
        Raises:
            BadRequest: If payload is invalid
        """
        try:
            # Validate payload structure
            if not validate_facebook_payload(data):
                raise BadRequest("Invalid Facebook payload structure")
            
            entry = data["entry"][0]
            
            if "messaging" in entry:
                for messaging_event in entry["messaging"]:
                    self._process_facebook_message(messaging_event)
                    
        except Exception as e:
            self.logger.error(f"Error processing Facebook message: {e}")
            raise
    
    def _process_whatsapp_message(self, message: Dict[str, Any], value: Dict[str, Any]) -> None:
        """Process individual WhatsApp message."""
        try:
            sender = message["from"]
            timestamp = message["timestamp"]
            message_id = message.get("id")
            
            # Extract message content based on type
            if message["type"] == "text":
                content = message["text"]["body"]
                message_type = "text"
            elif message["type"] == "image":
                content = f"[Image message] ID: {message['image']['id']}"
                message_type = "image"
            elif message["type"] == "document":
                content = f"[Document] {message['document'].get('filename', 'Unknown')}"
                message_type = "document"
            elif message["type"] == "audio":
                content = "[Audio message]"
                message_type = "audio"
            elif message["type"] == "video":
                content = "[Video message]"
                message_type = "video"
            else:
                content = f"[{message['type'].title()} message]"
                message_type = message["type"]
            
            # Resolve handling agent for incoming based on conversation
            handling_agent = self.message_service.resolve_incoming_agent(sender, "WhatsApp")

            # Prepare extra data
            extra_data = {
                "phone_number_id": value.get("metadata", {}).get("phone_number_id"),
                "display_phone_number": value.get("metadata", {}).get("display_phone_number"),
                "message_type": message["type"]
            }
            
            # Log message
            self.message_service.log_message(
                agent=handling_agent,
                platform="WhatsApp",
                recipient=sender,
                content=sanitize_input(content),
                message_type=message_type,
                message_id=message_id,
                sender_id=sender,
                is_incoming=True,
                status="received",
                extra_data=extra_data
            )
            
            self.logger.info(f"WhatsApp message processed - From: {sender}, Type: {message_type}")
            
        except Exception as e:
            self.logger.error(f"Error processing individual WhatsApp message: {e}")
            raise
    
    def _process_facebook_message(self, messaging_event: Dict[str, Any]) -> None:
        """Process individual Facebook Messenger message."""
        try:
            sender = messaging_event["sender"]["id"]
            timestamp = messaging_event["timestamp"]
            
            if "message" in messaging_event:
                message = messaging_event["message"]
                message_id = message.get("mid")
                
                if "text" in message:
                    content = message["text"]
                    message_type = "text"
                elif "attachments" in message:
                    content = f"[Attachment] Type: {message['attachments'][0]['type']}"
                    message_type = "attachment"
                else:
                    content = "[Unknown message type]"
                    message_type = "unknown"
                
                # Resolve handling agent based on conversation
                handling_agent = self.message_service.resolve_incoming_agent(sender, "Facebook")

                # Prepare extra data
                extra_data = {
                    "recipient_id": messaging_event.get("recipient", {}).get("id"),
                    "message_type": message_type
                }
                
                # Log message
                self.message_service.log_message(
                    agent=handling_agent,
                    platform="Facebook",
                    recipient=sender,
                    content=sanitize_input(content),
                    message_type=message_type,
                    message_id=message_id,
                    sender_id=sender,
                    is_incoming=True,
                    status="received",
                    extra_data=extra_data
                )
                
                self.logger.info(f"Facebook message processed - From: {sender}, Type: {message_type}")
                
            elif "postback" in messaging_event:
                # Handle postback events
                postback = messaging_event["postback"]
                content = f"[Postback] {postback['title']}: {postback['payload']}"
                
                self.message_service.log_message(
                    agent="Agent1",
                    platform="Facebook",
                    recipient=sender,
                    content=sanitize_input(content),
                    message_type="postback",
                    message_id=postback.get("mid"),
                    sender_id=sender,
                    is_incoming=True,
                    status="received",
                    extra_data={"postback_title": postback['title'], "postback_payload": postback['payload']}
                )
                
                self.logger.info(f"Facebook postback processed - From: {sender}")
                
        except Exception as e:
            self.logger.error(f"Error processing individual Facebook message: {e}")
            raise


# Initialize webhook handler
webhook_handler = WebhookHandler()


@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """
    Main webhook endpoint for Meta platforms.
    Handles both verification and message processing.
    """
    try:
        if request.method == 'GET':
            # Webhook verification
            verify_token = request.args.get("hub.verify_token")
            challenge = request.args.get("hub.challenge")
            
            if not verify_token or not challenge:
                logger.warning("Missing verification parameters")
                abort(400, "Missing verification parameters")
            
            return webhook_handler.handle_verification(verify_token, challenge)
        
        elif request.method == 'POST':
            # Message processing
            try:
                data = request.get_json()
                if not data:
                    logger.warning("Empty webhook payload")
                    abort(400, "Empty payload")
                
                logger.info(f"Received webhook data - Object: {data.get('object')}")
                
                # Route to appropriate handler
                if data.get("object") == "whatsapp_business_account":
                    webhook_handler.handle_whatsapp_message(data)
                elif data.get("object") == "page":
                    webhook_handler.handle_facebook_message(data)
                else:
                    logger.warning(f"Unknown webhook object type: {data.get('object')}")
                    abort(400, f"Unknown object type: {data.get('object')}")
                
                return jsonify({"status": "ok", "signature": "8598"}), 200
                
            except BadRequest as e:
                logger.warning(f"Bad request: {e}")
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                logger.error(f"Webhook processing error: {e}")
                return jsonify({"error": "Internal server error"}), 500
    
    except Exception as e:
        logger.error(f"Webhook endpoint error: {e}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    try:
        # Check database connectivity
        from ..database import db_manager
        db_healthy = db_manager.health_check()
        
        health_status = {
            "status": "healthy" if db_healthy else "unhealthy",
            "service": "HCTC-CRM Webhook",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "2.0.0",
            "signature": "8598",
            "database": "connected" if db_healthy else "disconnected"
        }
        
        status_code = 200 if db_healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "signature": "8598"
        }), 503


@app.route('/', methods=['GET'])
def home():
    """
    Home endpoint with system information.
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>HCTC-CRM Webhook System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .feature { margin: 20px 0; padding: 15px; background: #ecf0f1; border-radius: 5px; }
            .status { color: #27ae60; font-weight: bold; }
            .signature { color: #e74c3c; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 HCTC-CRM Webhook System</h1>
            <p class="status">✅ System Online - Signature: 8598</p>
            
            <div class="feature">
                <h3>📱 WhatsApp Business API Integration</h3>
                <p>Real-time message processing and agent tracking</p>
            </div>
            
            <div class="feature">
                <h3>📘 Facebook Messenger Integration</h3>
                <p>Complete Facebook Messenger support with analytics</p>
            </div>
            
            <div class="feature">
                <h3>📊 Advanced Analytics</h3>
                <p>Comprehensive reporting and performance metrics</p>
            </div>
            
            <h3>🔗 Endpoints:</h3>
            <ul>
                <li><strong>Webhook:</strong> /webhook</li>
                <li><strong>Health Check:</strong> <a href="/health">/health</a></li>
                <li><strong>Dashboard:</strong> <a href="http://localhost:8050">http://localhost:8050</a></li>
            </ul>
            
            <p class="signature">© 2025 - Signature: 8598 - Professional Call Center Management</p>
        </div>
    </body>
    </html>
    """


@app.route('/send', methods=['POST'])
def send_message():
    """
    Send a WhatsApp message via Cloud API and log it as an outgoing message.
    Expected JSON body: {"agent": "AgentName", "to": "+2547...", "text": "..."}
    """
    try:
        data = request.get_json(force=True, silent=False)
        agent = sanitize_input((data or {}).get('agent', ''))
        to = sanitize_input((data or {}).get('to', ''))
        text = (data or {}).get('text', '')

        if not agent or not to or not text:
            return jsonify({"error": "agent, to, and text are required", "signature": "8598"}), 400

        if not is_valid_phone_number(to):
            return jsonify({"error": "invalid phone number format (E.164)", "signature": "8598"}), 400

        # Extract initials from content and strip token for sending/logging
        cleaned_text, initials = extract_initials_and_strip(text)

        # Call WhatsApp Cloud API
        import requests
        url = f"https://graph.facebook.com/v18.0/{config.whatsapp.phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {config.whatsapp.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": to.lstrip('+'),
            "type": "text",
            "text": {"body": cleaned_text},
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=20)
        if resp.status_code >= 400:
            logger.error(f"WhatsApp send failed: {resp.status_code} {resp.text}")
            return jsonify({"error": "send_failed", "details": resp.text, "signature": "8598"}), 502

        # Log outgoing message
        try:
            message_id = (resp.json() or {}).get('messages', [{}])[0].get('id')
        except Exception:
            message_id = None

        get_message_service().log_message(
            agent=agent,
            platform="WhatsApp",
            recipient=to,
            content=sanitize_input(cleaned_text),
            message_type="text",
            message_id=message_id,
            sender_id=None,
            is_incoming=False,
            status="sent",
            extra_data={"provider": "cloud_api", "agent_initials": initials} if initials else {"provider": "cloud_api"}
        )

        return jsonify({"status": "ok", "message_id": message_id, "signature": "8598"}), 200

    except Exception as e:
        logger.error(f"/send error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.route('/reports/agent-daily-excel', methods=['GET'])
def agent_daily_excel():
    """
    Generate a daily Excel summary for a given agent containing:
    - Date
    - Agent display (INITIALS Name when available)
    - Messages handled (outgoing only)
    - Phone numbers handled (single cell, newline-separated)

    Query params:
      - date: YYYY-MM-DD (default: today in server timezone)
      - agent: Agent name (required)
    """
    try:
        from ..database import get_db_session, Message
        from datetime import datetime, timedelta
        import pandas as pd
        import json as _json
        from io import BytesIO

        agent_name = request.args.get('agent')
        date_str = request.args.get('date')

        if not agent_name:
            return jsonify({"error": "agent is required", "signature": "8598"}), 400

        if date_str:
            try:
                day = datetime.fromisoformat(date_str)
            except Exception:
                return jsonify({"error": "invalid date"}), 400
        else:
            day = datetime.now()

        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        with get_db_session() as s:
            rows = (
                s.query(Message)
                .filter(
                    Message.agent == agent_name,
                    Message.is_incoming == False,
                    Message.timestamp >= start,
                    Message.timestamp < end,
                )
                .all()
            )

        # Determine initials and phone numbers
        initials = None
        phone_numbers = []
        for m in rows:
            if m.recipient and m.recipient not in phone_numbers:
                phone_numbers.append(m.recipient)
            if not initials and m.extra_data:
                try:
                    ed = _json.loads(m.extra_data)
                    val = (ed or {}).get('agent_initials')
                    if val:
                        initials = val
                except Exception:
                    pass

        display = f"{initials} {agent_name}".strip() if initials else agent_name
        messages_handled = len(rows)
        phones_cell = "\n".join(phone_numbers)

        # Determine if agent is on leave that day
        from ..services import get_message_service as _gms
        svc = _gms()
        on_leave = svc.is_agent_on_leave(agent_name, start)

        df = pd.DataFrame([
            {
                "Date": start.strftime('%Y-%m-%d'),
                "Agent": display,
                "MessagesHandled": messages_handled,
                "PhoneNumbers": phones_cell,
                "OnLeave": on_leave,
            }
        ])

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Summary')
        buffer.seek(0)

        filename = f"agent_daily_{agent_name}_{start.strftime('%Y%m%d')}.xlsx"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"/reports/agent-daily-excel error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.route('/reports/agent-handled-daily-excel', methods=['GET'])
def agent_handled_daily_excel():
    """
    Daily agent handling report (incoming messages associated to agent):
    - Date
    - Agent
    - MessagesHandled (incoming only)
    - PhoneNumbers (newline-separated unique recipients)

    Query params:
      - date: YYYY-MM-DD (default today)
      - agent: Agent name (required)
    """
    try:
        from ..database import get_db_session, Message
        from datetime import datetime, timedelta
        import pandas as pd
        from io import BytesIO

        agent_name = request.args.get('agent')
        date_str = request.args.get('date')

        if not agent_name:
            return jsonify({"error": "agent is required", "signature": "8598"}), 400

        if date_str:
            try:
                day = datetime.fromisoformat(date_str)
            except Exception:
                return jsonify({"error": "invalid date"}), 400
        else:
            day = datetime.now()

        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        with get_db_session() as s:
            rows = (
                s.query(Message)
                .filter(
                    Message.agent == agent_name,
                    Message.is_incoming == True,
                    Message.timestamp >= start,
                    Message.timestamp < end,
                )
                .all()
            )

        phone_numbers = []
        for m in rows:
            if m.recipient and m.recipient not in phone_numbers:
                phone_numbers.append(m.recipient)

        # Determine if agent is on leave that day
        from ..services import get_message_service as _gms
        svc = _gms()
        on_leave = svc.is_agent_on_leave(agent_name, start)

        df = pd.DataFrame([
            {
                "Date": start.strftime('%Y-%m-%d'),
                "Agent": agent_name,
                "MessagesHandled": len(rows),
                "PhoneNumbers": "\n".join(phone_numbers),
                "OnLeave": on_leave,
            }
        ])

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Handled')
        buffer.seek(0)

        filename = f"agent_handled_{agent_name}_{start.strftime('%Y%m%d')}.xlsx"
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        logger.error(f"/reports/agent-handled-daily-excel error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.route('/team/schedules/availability', methods=['GET'])
def schedules_availability():
    """Get current availability for a list of agents. Query: agents=Agent1,Agent2"""
    try:
        names = (request.args.get('agents') or '').split(',')
        names = [n.strip() for n in names if n.strip()]
        if not names:
            return jsonify({"error": "agents required", "signature": "8598"}), 400
        svc = get_message_service()
        result = [svc.get_agent_availability(a) for a in names]
        return jsonify({"data": result, "signature": "8598"}), 200
    except Exception as e:
        logger.error(f"/team/schedules/availability error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.route('/team/schedules/import', methods=['POST'])
def schedules_import():
    """Import schedules from JSON payload: {items: [{agent, date, shift_start, shift_end, role?, notes?}, ...]}"""
    try:
        from ..database import get_db_session, AgentSchedule
        import json as _j
        data = request.get_json(silent=True) or {}
        items = data.get('items') or []
        if not isinstance(items, list) or not items:
            return jsonify({"error": "items list required", "signature": "8598"}), 400
        created = 0
        with get_db_session() as s:
            from datetime import datetime
            for itm in items:
                try:
                    agent = str(itm.get('agent') or '').strip()
                    date_s = itm.get('date')
                    start_s = itm.get('shift_start')
                    end_s = itm.get('shift_end')
                    if not agent or not date_s or not start_s or not end_s:
                        continue
                    date = datetime.fromisoformat(date_s)
                    shift_start = datetime.fromisoformat(start_s)
                    shift_end = datetime.fromisoformat(end_s)
                    role = (itm.get('role') or None)
                    notes = (itm.get('notes') or None)
                    s.add(AgentSchedule(agent=agent, date=date, shift_start=shift_start, shift_end=shift_end, role=role, notes=notes))
                    created += 1
                except Exception:
                    continue
        return jsonify({"status": "ok", "created": created, "signature": "8598"}), 200
    except Exception as e:
        logger.error(f"/team/schedules/import error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.route('/team/schedules/export', methods=['GET'])
def schedules_export():
    """Export schedules as CSV. Query: start=YYYY-MM-DD, end=YYYY-MM-DD, agent(optional)."""
    try:
        from ..database import get_db_session, AgentSchedule
        from datetime import datetime, timedelta
        import pandas as pd
        from io import StringIO
        start_s = request.args.get('start')
        end_s = request.args.get('end')
        agent = request.args.get('agent')
        if not start_s or not end_s:
            return jsonify({"error": "start and end required", "signature": "8598"}), 400
        start = datetime.fromisoformat(start_s)
        end = datetime.fromisoformat(end_s) + timedelta(days=1)
        with get_db_session() as s:
            q = s.query(AgentSchedule).filter(AgentSchedule.date >= start, AgentSchedule.date < end)
            if agent:
                q = q.filter(AgentSchedule.agent == agent)
            rows = q.all()
        df = pd.DataFrame([r.to_dict() for r in rows]) if rows else pd.DataFrame(columns=["agent","date","shift_start","shift_end","role","notes"])
        csv_buf = StringIO()
        df.to_csv(csv_buf, index=False)
        csv_buf.seek(0)
        return app.response_class(csv_buf.getvalue(), mimetype='text/csv')
    except Exception as e:
        logger.error(f"/team/schedules/export error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.route('/team/leaves', methods=['POST'])
def create_leave():
    """Create a leave record. JSON: {agent, start_date, end_date, reason?, status?} default status=approved."""
    try:
        from ..database import get_db_session, AgentLeave
        from datetime import datetime
        body = request.get_json(force=True)
        agent = (body.get('agent') or '').strip()
        start_s = body.get('start_date')
        end_s = body.get('end_date')
        reason = (body.get('reason') or None)
        status = (body.get('status') or 'approved')
        if not agent or not start_s or not end_s:
            return jsonify({"error": "agent, start_date, end_date required", "signature": "8598"}), 400
        start = datetime.fromisoformat(start_s)
        end = datetime.fromisoformat(end_s)
        with get_db_session() as s:
            s.add(AgentLeave(agent=agent, start_date=start, end_date=end, reason=reason, status=status))
        return jsonify({"status": "ok", "signature": "8598"}), 200
    except Exception as e:
        logger.error(f"/team/leaves error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.route('/reports/agent-replies', methods=['GET'])
def agent_replies_report():
    """
    Per-agent reply counts and distinct recipients replied to.
    Query params: start=YYYY-MM-DD, end=YYYY-MM-DD (optional)
    """
    try:
        from sqlalchemy import func, distinct
        from ..database import get_db_session, Message
        from datetime import datetime

        start = request.args.get('start')
        end = request.args.get('end')

        with get_db_session() as s:
            q = s.query(
                Message.agent.label('agent'),
                func.count().label('outgoing_count'),
                func.count(distinct(Message.recipient)).label('recipients_replied_to'),
            ).filter(Message.is_incoming == False)

            if start:
                try:
                    start_dt = datetime.fromisoformat(start)
                    q = q.filter(Message.timestamp >= start_dt)
                except Exception:
                    return jsonify({"error": "invalid start date"}), 400
            if end:
                try:
                    end_dt = datetime.fromisoformat(end)
                    q = q.filter(Message.timestamp <= end_dt)
                except Exception:
                    return jsonify({"error": "invalid end date"}), 400

            rows = q.group_by(Message.agent).all()
            result = [
                {
                    "agent": r.agent,
                    "outgoing_count": int(r.outgoing_count or 0),
                    "recipients_replied_to": int(r.recipients_replied_to or 0),
                }
                for r in rows
            ]

        return jsonify({"data": result, "signature": "8598"}), 200

    except Exception as e:
        logger.error(f"/reports/agent-replies error: {e}")
        return jsonify({"error": "internal_error", "signature": "8598"}), 500


@app.errorhandler(400)
def bad_request(error):
    """Handle bad request errors."""
    return jsonify({"error": "Bad request", "signature": "8598"}), 400


@app.errorhandler(401)
def unauthorized(error):
    """Handle unauthorized errors."""
    return jsonify({"error": "Unauthorized", "signature": "8598"}), 401


@app.errorhandler(404)
def not_found(error):
    """Handle not found errors."""
    return jsonify({"error": "Not found", "signature": "8598"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    return jsonify({"error": "Internal server error", "signature": "8598"}), 500


if __name__ == "__main__":
    # Initialize database
    from ..database import init_database
    init_database()
    
    # Start application
    logger.info(f"Starting HCTC-CRM Webhook Server - Signature: 8598")
    app.run(
        host=config.webhook.host,
        port=config.webhook.port,
        debug=config.webhook.debug
    )
