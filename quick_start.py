#!/usr/bin/env python3
"""
Quick Start Script for WhatsApp and Facebook Messenger
This script shows how to send messages using the messaging system
"""

from messaging import WhatsAppMessenger, FacebookMessenger, send_auto_reply
import time

def demo_whatsapp_messaging():
    """Demonstrate WhatsApp messaging capabilities"""
    print("📱 WhatsApp Messaging Demo")
    print("-" * 30)
    
    # Initialize WhatsApp messenger
    whatsapp = WhatsAppMessenger()
    
    # Example phone number (replace with actual number for testing)
    test_phone = "+1234567890"  # Replace with real number
    
    print(f"1. Sending text message to {test_phone}...")
    
    # Send a simple text message
    result = whatsapp.send_text_message(test_phone, "Hello! This is a test message from your call center system.")
    
    if result["success"]:
        print(f"✅ Message sent successfully! Message ID: {result.get('message_id', 'N/A')}")
    else:
        print(f"❌ Failed to send message: {result.get('error', 'Unknown error')}")
    
    print("\n2. Sending template message...")
    
    # Send a template message (you need to create templates in Meta dashboard first)
    template_result = whatsapp.send_template_message(
        test_phone, 
        "hello_world",  # Template name from Meta dashboard
        "en_US"
    )
    
    if template_result["success"]:
        print(f"✅ Template message sent successfully!")
    else:
        print(f"❌ Template message failed: {template_result.get('error', 'Unknown error')}")
    
    print()

def demo_facebook_messaging():
    """Demonstrate Facebook Messenger capabilities"""
    print("📘 Facebook Messenger Demo")
    print("-" * 30)
    
    # Initialize Facebook messenger
    facebook = FacebookMessenger()
    
    # Example user ID (replace with actual user ID for testing)
    test_user_id = "123456789"  # Replace with real user ID
    
    print(f"1. Sending text message to user {test_user_id}...")
    
    # Send a simple text message
    result = facebook.send_text_message(test_user_id, "Hello! This is a test message from your call center system.")
    
    if result["success"]:
        print(f"✅ Message sent successfully! Message ID: {result.get('message_id', 'N/A')}")
    else:
        print(f"❌ Failed to send message: {result.get('error', 'Unknown error')}")
    
    print("\n2. Sending message with quick replies...")
    
    # Send a message with quick reply buttons
    quick_replies = [
        {
            "content_type": "text",
            "title": "Yes, please help",
            "payload": "HELP_YES"
        },
        {
            "content_type": "text", 
            "title": "No, I'm good",
            "payload": "HELP_NO"
        }
    ]
    
    quick_reply_result = facebook.send_quick_replies(
        test_user_id,
        "Would you like help with anything?",
        quick_replies
    )
    
    if quick_reply_result["success"]:
        print(f"✅ Quick reply message sent successfully!")
    else:
        print(f"❌ Quick reply message failed: {quick_reply_result.get('error', 'Unknown error')}")
    
    print()

def demo_auto_reply():
    """Demonstrate automatic reply system"""
    print("🔄 Auto-Reply System Demo")
    print("-" * 30)
    
    # Example scenarios
    scenarios = [
        ("WhatsApp", "+1234567890", "Thanks for your message! We'll get back to you within 24 hours."),
        ("Facebook", "123456789", "Hello! How can we assist you today?"),
        ("WhatsApp", "+1987654321", "Your inquiry has been received. Our team will contact you soon.")
    ]
    
    for i, (platform, recipient, message) in enumerate(scenarios, 1):
        print(f"{i}. Sending auto-reply to {platform} user {recipient}...")
        
        result = send_auto_reply(platform, recipient, message)
        
        if result["success"]:
            print(f"   ✅ Auto-reply sent successfully!")
        else:
            print(f"   ❌ Auto-reply failed: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)  # Small delay between messages
    
    print()

def show_setup_instructions():
    """Show setup instructions"""
    print("🔧 Setup Instructions")
    print("=" * 50)
    print("Before running this demo, make sure you have:")
    print()
    print("1. ✅ Updated config.py with your real API credentials")
    print("2. ✅ Set up webhook in Meta Developer Dashboard")
    print("3. ✅ Used ngrok to expose your local server")
    print("4. ✅ Tested webhook connectivity")
    print()
    print("📚 For detailed setup instructions, see SETUP_GUIDE.md")
    print()

def main():
    """Main demo function"""
    print("🚀 WhatsApp + Facebook Messenger Quick Start Demo")
    print("=" * 60)
    print()
    
    # Show setup instructions first
    show_setup_instructions()
    
    # Check if user wants to continue
    response = input("Do you want to continue with the demo? (y/n): ").lower().strip()
    
    if response != 'y':
        print("Demo cancelled. Please complete setup first.")
        return
    
    print("\n" + "=" * 60)
    print("🎬 Starting Demo...")
    print()
    
    try:
        # Run demos
        demo_whatsapp_messaging()
        demo_facebook_messaging()
        demo_auto_reply()
        
        print("=" * 60)
        print("🎉 Demo completed successfully!")
        print()
        print("💡 Next steps:")
        print("   • Replace test phone numbers/user IDs with real ones")
        print("   • Customize your auto-reply messages")
        print("   • Integrate with your call center workflow")
        print("   • Monitor message delivery in Meta dashboard")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Check your API credentials in config.py")
        print("   • Ensure your Flask app is running")
        print("   • Verify webhook connectivity")
        print("   • Check console logs for detailed errors")

if __name__ == "__main__":
    main()

