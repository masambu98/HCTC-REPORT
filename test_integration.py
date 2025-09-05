#!/usr/bin/env python3
"""
Test script for WhatsApp and Facebook Messenger integration
This script simulates webhook calls to test your system
"""

import requests
import json
from datetime import datetime

# Test configuration
WEBHOOK_URL = "http://localhost:5000/webhook"
VERIFY_TOKEN = "callcenter_verify_123"  # Should match config.py

def test_webhook_verification():
    """Test the GET webhook verification"""
    print("🔍 Testing webhook verification...")
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": VERIFY_TOKEN,
        "hub.challenge": "test_challenge_123"
    }
    
    try:
        response = requests.get(WEBHOOK_URL, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200 and response.text == "test_challenge_123":
            print("✅ Webhook verification successful!")
        else:
            print("❌ Webhook verification failed!")
            
    except Exception as e:
        print(f"❌ Error testing webhook verification: {e}")

def test_whatsapp_webhook():
    """Test WhatsApp webhook message processing"""
    print("\n📱 Testing WhatsApp webhook...")
    
    # Simulate WhatsApp message webhook
    whatsapp_payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "+1234567890",
                                "phone_number_id": "987654321"
                            },
                            "messages": [
                                {
                                    "from": "+1234567890",
                                    "id": "test_message_id",
                                    "timestamp": str(int(datetime.now().timestamp())),
                                    "type": "text",
                                    "text": {
                                        "body": "Hello! This is a test message from WhatsApp."
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=whatsapp_payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ WhatsApp webhook test successful!")
        else:
            print("❌ WhatsApp webhook test failed!")
            
    except Exception as e:
        print(f"❌ Error testing WhatsApp webhook: {e}")

def test_facebook_webhook():
    """Test Facebook Messenger webhook message processing"""
    print("\n📘 Testing Facebook Messenger webhook...")
    
    # Simulate Facebook message webhook
    facebook_payload = {
        "object": "page",
        "entry": [
            {
                "id": "123456789",
                "time": int(datetime.now().timestamp()),
                "messaging": [
                    {
                        "sender": {
                            "id": "123456789"
                        },
                        "recipient": {
                            "id": "987654321"
                        },
                        "timestamp": int(datetime.now().timestamp()),
                        "message": {
                            "mid": "test_message_id",
                            "text": "Hello! This is a test message from Facebook Messenger."
                        }
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=facebook_payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Facebook webhook test successful!")
        else:
            print("❌ Facebook webhook test failed!")
            
    except Exception as e:
        print(f"❌ Error testing Facebook webhook: {e}")

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Health endpoint working!")
        else:
            print("❌ Health endpoint failed!")
            
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting integration tests...")
    print("=" * 50)
    
    # Make sure your Flask app is running first!
    print("⚠️  IMPORTANT: Make sure your Flask app is running on localhost:5000")
    print("   Run: python app.py")
    print("=" * 50)
    
    try:
        test_health_endpoint()
        test_webhook_verification()
        test_whatsapp_webhook()
        test_facebook_webhook()
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        print("\nNext steps:")
        print("1. Update config.py with your real API credentials")
        print("2. Set up webhook in Meta Developer Dashboard")
        print("3. Use ngrok to expose your server")
        print("4. Test with real messages!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()

