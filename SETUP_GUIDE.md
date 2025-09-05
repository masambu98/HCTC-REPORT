# WhatsApp + Facebook Messenger Integration Setup Guide

This guide will walk you through setting up real-time messaging integration with WhatsApp Business API and Facebook Messenger for your call center system.

## 🚀 Prerequisites

- Python 3.7+ installed
- A Facebook Developer account
- A WhatsApp Business account (or test number)
- A Facebook Page for your business
- ngrok (for exposing your local server)

## 📋 Step-by-Step Setup

### 1. Meta Developer Account Setup

1. **Go to [Facebook Developers](https://developers.facebook.com)**
2. **Log in with your Facebook account**
3. **Click "Create App" → Select "Business" type**
4. **Fill in your app details and create the app**

### 2. WhatsApp Business API Setup

1. **In your app dashboard, go to "Add Product"**
2. **Find and click "WhatsApp" → "Set Up"**
3. **Complete the setup process**
4. **Note down your:**
   - **Phone Number ID**
   - **WhatsApp Business Account ID**
   - **Access Token (temporary)**

### 3. Facebook Messenger Setup

1. **In your app dashboard, go to "Add Product"**
2. **Find and click "Messenger" → "Set Up"**
3. **Connect your Facebook Page**
4. **Note down your:**
   - **Page ID**
   - **Page Access Token**

### 4. Update Configuration

Edit `config.py` with your actual credentials:

```python
# Replace these with your actual values
WHATSAPP_TOKEN = "YOUR_ACTUAL_WHATSAPP_TOKEN"
WHATSAPP_PHONE_ID = "YOUR_ACTUAL_PHONE_ID"
WHATSAPP_BUSINESS_ACCOUNT_ID = "YOUR_ACTUAL_BUSINESS_ACCOUNT_ID"

FACEBOOK_PAGE_TOKEN = "YOUR_ACTUAL_PAGE_TOKEN"
FACEBOOK_PAGE_ID = "YOUR_ACTUAL_PAGE_ID"

# Change this to a random string
VERIFY_TOKEN = "your_random_string_here"
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Expose Your Local Server

Since Meta needs to reach your webhook, you need to expose your local server:

```bash
# Install ngrok (if not already installed)
# Download from https://ngrok.com/download

# Expose your Flask app
ngrok http 5000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

### 7. Configure Webhook in Meta Dashboard

#### For WhatsApp:
1. **Go to WhatsApp → Configuration**
2. **Set Webhook URL:** `https://abc123.ngrok.io/webhook`
3. **Set Verify Token:** (same as in your config.py)
4. **Subscribe to fields:** `messages`

#### For Facebook Messenger:
1. **Go to Messenger → Settings**
2. **Set Webhook URL:** `https://abc123.ngrok.io/webhook`
3. **Set Verify Token:** (same as in your config.py)
4. **Subscribe to fields:** `messages`, `messaging_postbacks`

### 8. Test the Integration

1. **Start your Flask app:**
   ```bash
   python app.py
   ```

2. **Send a test message from WhatsApp or Facebook to your business account**

3. **Check your console logs** - you should see webhook data being processed

4. **Check your database** - messages should be logged automatically

## 🔧 Troubleshooting

### Common Issues:

1. **"Verification failed" error:**
   - Check that your `VERIFY_TOKEN` matches exactly in both config.py and Meta dashboard

2. **"Webhook not receiving messages":**
   - Ensure ngrok is running and URL is correct
   - Check that you've subscribed to the correct fields
   - Verify your access tokens are valid

3. **"Permission denied" errors:**
   - Ensure your app has the necessary permissions
   - Check that your tokens haven't expired

### Testing Webhook:

Visit `https://abc123.ngrok.io/` to see the setup instructions and verify your server is running.

## 📱 Message Types Supported

### WhatsApp:
- ✅ Text messages
- ✅ Image messages
- ✅ Template messages (for sending)

### Facebook Messenger:
- ✅ Text messages
- ✅ Attachments
- ✅ Postback events (button clicks)

## 🔄 Auto-Reply System

The system includes an auto-reply feature. You can customize responses in `messaging.py`:

```python
# Example: Send automatic welcome message
from messaging import send_auto_reply

# This will automatically reply to incoming messages
send_auto_reply("WhatsApp", "+1234567890", "Thanks for your message! We'll get back to you soon.")
```

## 📊 Monitoring

- **Health Check:** Visit `/health` endpoint
- **Logs:** Check console output for detailed logging
- **Database:** All messages are stored in `callcenter.db`

## 🚨 Security Notes

- **Never commit your actual tokens to version control**
- **Use environment variables for production**
- **Regularly rotate your access tokens**
- **Monitor webhook usage and implement rate limiting if needed**

## 📞 Support

If you encounter issues:
1. Check the console logs for error messages
2. Verify all credentials are correct
3. Ensure ngrok is running and accessible
4. Check Meta Developer Dashboard for any error messages

---

**🎉 Congratulations!** Your call center system is now connected to WhatsApp and Facebook Messenger. Messages will flow automatically into your database, and you can send replies using the messaging utilities.

