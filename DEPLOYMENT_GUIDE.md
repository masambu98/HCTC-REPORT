# 🚀 HCTC-CRM Deployment Guide

**Copyright (c) 2025 - Signature: 8598**

Complete deployment guide for the HCTC-CRM Professional WhatsApp & Facebook Messenger Integration Platform.

## 🌐 Render Deployment (Recommended)

### Prerequisites
- Render account
- GitHub repository with HCTC-CRM code
- WhatsApp Business API credentials
- Facebook Page credentials

### Step 1: Prepare Repository

1. **Fork or clone the repository**
2. **Ensure all files are committed**
3. **Verify render.yaml is present**

### Step 2: Create Render Services

#### Database Service
1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Name: `hctc-crm-db`
4. Plan: Starter (Free) or higher
5. Region: Choose closest to your users
6. Click "Create Database"

#### Webhook Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Name: `hctc-crm-webhook`
4. Environment: Python 3
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python app.py`
7. Plan: Starter (Free) or higher

#### Dashboard Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Name: `hctc-crm-dashboard`
4. Environment: Python 3
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python dashboard.py`
7. Plan: Starter (Free) or higher

### Step 3: Configure Environment Variables

#### Webhook Service Variables
```bash
ENVIRONMENT=production
HOST=0.0.0.0
PORT=5000
DATABASE_URL=<from database service>
WHATSAPP_ACCESS_TOKEN=<your_token>
WHATSAPP_PHONE_ID=<your_phone_id>
WHATSAPP_BUSINESS_ACCOUNT_ID=<your_business_id>
FACEBOOK_PAGE_ACCESS_TOKEN=<your_page_token>
FACEBOOK_PAGE_ID=<your_page_id>
META_APP_ID=<your_app_id>
META_APP_SECRET=<your_app_secret>
WEBHOOK_VERIFY_TOKEN=<generate_random_string>
FLASK_SECRET_KEY=<generate_random_string>
LOG_LEVEL=INFO
```

#### Dashboard Service Variables
```bash
ENVIRONMENT=production
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=8050
DATABASE_URL=<from database service>
```

### Step 4: Deploy Services

1. **Deploy Database first**
2. **Wait for database to be ready**
3. **Deploy Webhook service**
4. **Deploy Dashboard service**

### Step 5: Configure Webhooks

#### WhatsApp Business API
1. Go to Meta Developer Console
2. Select your WhatsApp Business app
3. Go to Configuration → Webhooks
4. Callback URL: `https://your-webhook-service.onrender.com/webhook`
5. Verify Token: Use the same value as `WEBHOOK_VERIFY_TOKEN`
6. Subscribe to `messages` events

#### Facebook Messenger
1. Go to Meta Developer Console
2. Select your Facebook app
3. Go to Messenger → Settings
4. Webhooks URL: `https://your-webhook-service.onrender.com/webhook`
5. Verify Token: Use the same value as `WEBHOOK_VERIFY_TOKEN`
6. Subscribe to `messages` and `messaging_postbacks`

### Step 6: Test Deployment

1. **Check webhook health**: `https://your-webhook-service.onrender.com/health`
2. **Access dashboard**: `https://your-dashboard-service.onrender.com`
3. **Send test message** to your WhatsApp number
4. **Verify message appears** in dashboard

## 🐳 Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose installed

### Step 1: Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 8050

CMD ["python", "app.py"]
```

### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  webhook:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/hctc_crm
      - WHATSAPP_ACCESS_TOKEN=${WHATSAPP_ACCESS_TOKEN}
      - WHATSAPP_PHONE_ID=${WHATSAPP_PHONE_ID}
      - WHATSAPP_BUSINESS_ACCOUNT_ID=${WHATSAPP_BUSINESS_ACCOUNT_ID}
      - FACEBOOK_PAGE_ACCESS_TOKEN=${FACEBOOK_PAGE_ACCESS_TOKEN}
      - FACEBOOK_PAGE_ID=${FACEBOOK_PAGE_ID}
      - META_APP_ID=${META_APP_ID}
      - META_APP_SECRET=${META_APP_SECRET}
      - WEBHOOK_VERIFY_TOKEN=${WEBHOOK_VERIFY_TOKEN}
      - FLASK_SECRET_KEY=${FLASK_SECRET_KEY}
    depends_on:
      - db

  dashboard:
    build: .
    command: python dashboard.py
    ports:
      - "8050:8050"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/hctc_crm
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=hctc_crm
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Step 3: Deploy with Docker

```bash
# Create .env file with your credentials
cp .env.example .env

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

## 🖥️ VPS Deployment

### Prerequisites
- Ubuntu 20.04+ VPS
- Root access
- Domain name (optional)

### Step 1: Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y
```

### Step 2: Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE hctc_crm;
CREATE USER hctc_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE hctc_crm TO hctc_user;
\q
```

### Step 3: Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/hctc-crm
sudo chown $USER:$USER /opt/hctc-crm
cd /opt/hctc-crm

# Clone repository
git clone <your-repo-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from src.database import init_database; init_database()"
```

### Step 4: Systemd Services

#### Webhook Service
Create `/etc/systemd/system/hctc-webhook.service`:

```ini
[Unit]
Description=HCTC-CRM Webhook Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/hctc-crm
Environment=PATH=/opt/hctc-crm/venv/bin
Environment=DATABASE_URL=postgresql://hctc_user:your_secure_password@localhost/hctc_crm
Environment=WHATSAPP_ACCESS_TOKEN=your_token
Environment=WHATSAPP_PHONE_ID=your_phone_id
Environment=WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_id
Environment=FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token
Environment=FACEBOOK_PAGE_ID=your_page_id
Environment=META_APP_ID=your_app_id
Environment=META_APP_SECRET=your_app_secret
Environment=WEBHOOK_VERIFY_TOKEN=your_verify_token
Environment=FLASK_SECRET_KEY=your_secret_key
Environment=ENVIRONMENT=production
Environment=HOST=0.0.0.0
Environment=PORT=5000
ExecStart=/opt/hctc-crm/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Dashboard Service
Create `/etc/systemd/system/hctc-dashboard.service`:

```ini
[Unit]
Description=HCTC-CRM Dashboard Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/hctc-crm
Environment=PATH=/opt/hctc-crm/venv/bin
Environment=DATABASE_URL=postgresql://hctc_user:your_secure_password@localhost/hctc_crm
Environment=ENVIRONMENT=production
Environment=DASHBOARD_HOST=0.0.0.0
Environment=DASHBOARD_PORT=8050
ExecStart=/opt/hctc-crm/venv/bin/python dashboard.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### Step 5: Start Services

```bash
# Enable and start services
sudo systemctl enable hctc-webhook
sudo systemctl enable hctc-dashboard
sudo systemctl start hctc-webhook
sudo systemctl start hctc-dashboard

# Check status
sudo systemctl status hctc-webhook
sudo systemctl status hctc-dashboard
```

### Step 6: Nginx Configuration

Create `/etc/nginx/sites-available/hctc-crm`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /webhook {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/hctc-crm /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection string | Yes | - |
| `WHATSAPP_ACCESS_TOKEN` | WhatsApp Business API token | Yes | - |
| `WHATSAPP_PHONE_ID` | WhatsApp phone number ID | Yes | - |
| `WHATSAPP_BUSINESS_ACCOUNT_ID` | WhatsApp business account ID | Yes | - |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Facebook Page access token | Yes | - |
| `FACEBOOK_PAGE_ID` | Facebook Page ID | Yes | - |
| `META_APP_ID` | Meta App ID | Yes | - |
| `META_APP_SECRET` | Meta App Secret | Yes | - |
| `WEBHOOK_VERIFY_TOKEN` | Webhook verification token | Yes | - |
| `FLASK_SECRET_KEY` | Flask secret key | Yes | - |
| `ENVIRONMENT` | Environment (development/production) | No | development |
| `HOST` | Webhook host | No | 0.0.0.0 |
| `PORT` | Webhook port | No | 5000 |
| `DASHBOARD_PORT` | Dashboard port | No | 8050 |
| `LOG_LEVEL` | Logging level | No | INFO |

### Database Configuration

#### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

#### SQLite (Development)
```bash
DATABASE_URL=sqlite:///callcenter.db
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Database Connection Failed
```bash
# Check database status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U hctc_user -d hctc_crm

# Check logs
sudo journalctl -u hctc-webhook -f
```

#### 2. Webhook Not Receiving Messages
```bash
# Check webhook health
curl https://your-domain.com/health

# Check webhook logs
sudo journalctl -u hctc-webhook -f

# Verify webhook configuration in Meta Developer Console
```

#### 3. Dashboard Not Loading
```bash
# Check dashboard service
sudo systemctl status hctc-dashboard

# Check logs
sudo journalctl -u hctc-dashboard -f

# Check port availability
netstat -tlnp | grep 8050
```

#### 4. Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/hctc-crm

# Fix permissions
sudo chmod -R 755 /opt/hctc-crm
```

### Log Locations

- **System logs**: `sudo journalctl -u hctc-webhook -f`
- **Application logs**: `/opt/hctc-crm/logs/`
- **Nginx logs**: `/var/log/nginx/`
- **PostgreSQL logs**: `/var/log/postgresql/`

## 📊 Monitoring

### Health Checks

- **Webhook Health**: `https://your-domain.com/health`
- **Dashboard**: `https://your-domain.com/`

### Performance Monitoring

```bash
# Check service status
sudo systemctl status hctc-webhook hctc-dashboard

# Check resource usage
htop

# Check database connections
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

## 🔄 Updates

### Updating Application

```bash
# Stop services
sudo systemctl stop hctc-webhook hctc-dashboard

# Backup database
sudo -u postgres pg_dump hctc_crm > backup_$(date +%Y%m%d).sql

# Update code
cd /opt/hctc-crm
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Start services
sudo systemctl start hctc-webhook hctc-dashboard
```

## 🆘 Support

### Getting Help

1. **Check logs** for error messages
2. **Verify configuration** matches requirements
3. **Test webhook** with health check endpoint
4. **Contact support** with detailed error information

### Professional Support

For enterprise support and custom development:
- **Email**: support@hctc-crm.com
- **Documentation**: https://docs.hctc-crm.com
- **Status Page**: https://status.hctc-crm.com

---

**Ready to deploy? Follow this guide and have your professional call center system running in minutes!**

*Signature: 8598 - Professional Call Center Management Solutions*
