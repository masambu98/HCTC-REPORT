import requests
import json
import logging
from config import (
    WHATSAPP_ACCESS_TOKEN,
    WHATSAPP_PHONE_ID,
    FACEBOOK_PAGE_ACCESS_TOKEN,
    FACEBOOK_PAGE_ID
)

logger = logging.getLogger(__name__)

class WhatsAppMessenger:
    """Handle sending messages via WhatsApp Business API"""
    
    def __init__(self):
        self.token = WHATSAPP_ACCESS_TOKEN
        self.phone_id = WHATSAPP_PHONE_ID
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def send_text_message(self, recipient_phone, message_text):
        """Send a text message to a WhatsApp user"""
        try:
            url = f"{self.base_url}/{self.phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "text",
                "text": {"body": message_text}
            }
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in (200, 201):
                logger.info(f"WhatsApp message sent successfully to {recipient_phone}")
                return {"success": True, "message_id": response.json().get("messages", [{}])[0].get("id")}
            else:
                logger.error(f"WhatsApp message failed: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_template_message(self, recipient_phone, template_name, language_code="en_US", components=None):
        """Send a template message to a WhatsApp user"""
        try:
            url = f"{self.base_url}/{self.phone_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": recipient_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code}
                }
            }
            
            if components:
                payload["template"]["components"] = components
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code in (200, 201):
                logger.info(f"WhatsApp template message sent successfully to {recipient_phone}")
                return {"success": True, "message_id": response.json().get("messages", [{}])[0].get("id")}
            else:
                logger.error(f"WhatsApp template message failed: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp template message: {str(e)}")
            return {"success": False, "error": str(e)}

class FacebookMessenger:
    """Handle sending messages via Facebook Messenger API"""
    
    def __init__(self):
        self.token = FACEBOOK_PAGE_ACCESS_TOKEN
        self.page_id = FACEBOOK_PAGE_ID
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def send_text_message(self, recipient_id, message_text):
        """Send a text message to a Facebook user"""
        try:
            url = f"{self.base_url}/{self.page_id}/messages"
            
            payload = {
                "recipient": {"id": recipient_id},
                "message": {"text": message_text}
            }
            
            params = {"access_token": self.token}
            
            response = requests.post(url, json=payload, params=params)
            
            if response.status_code in (200, 201):
                logger.info(f"Facebook message sent successfully to {recipient_id}")
                return {"success": True, "message_id": response.json().get("message_id")}
            else:
                logger.error(f"Facebook message failed: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error sending Facebook message: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def send_quick_replies(self, recipient_id, message_text, quick_replies):
        """Send a message with quick reply buttons"""
        try:
            url = f"{self.base_url}/{self.page_id}/messages"
            
            payload = {
                "recipient": {"id": recipient_id},
                "message": {
                    "text": message_text,
                    "quick_replies": quick_replies
                }
            }
            
            params = {"access_token": self.token}
            
            response = requests.post(url, json=payload, params=params)
            
            if response.status_code in (200, 201):
                logger.info(f"Facebook quick reply message sent successfully to {recipient_id}")
                return {"success": True, "message_id": response.json().get("message_id")}
            else:
                logger.error(f"Facebook quick reply message failed: {response.status_code} - {response.text}")
                return {"success": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"Error sending Facebook quick reply message: {str(e)}")
            return {"success": False, "error": str(e)}

# Example usage functions

def send_whatsapp_reply(phone_number, message):
    """Helper function to send WhatsApp reply"""
    messenger = WhatsAppMessenger()
    return messenger.send_text_message(phone_number, message)


def send_facebook_reply(user_id, message):
    """Helper function to send Facebook reply"""
    messenger = FacebookMessenger()
    return messenger.send_text_message(user_id, message)


def send_auto_reply(platform, recipient, message):
    """Send automatic reply based on platform"""
    if platform.lower() == "whatsapp":
        return send_whatsapp_reply(recipient, message)
    elif platform.lower() == "facebook":
        return send_facebook_reply(recipient, message)
    else:
        logger.error(f"Unsupported platform: {platform}")
        return {"success": False, "error": f"Unsupported platform: {platform}"}
