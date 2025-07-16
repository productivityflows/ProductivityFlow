# ProductivityFlow SaaS - Complete Setup Guide

![ProductivityFlow Logo](https://via.placeholder.com/400x100/4338ca/ffffff?text=ProductivityFlow)

## 🚀 Overview

ProductivityFlow is a comprehensive SaaS productivity tracking platform that provides:

- **Employee Time Tracking** with AI-powered productivity reports
- **Manager Dashboard** with real-time analytics and billing
- **Stripe Payment Integration** ($9.99/employee/month)
- **Claude AI Integration** for hourly productivity summaries
- **Desktop Applications** for Windows and Mac
- **Auto-updater System** for seamless updates
- **Enhanced Security** with encrypted API key storage

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Backend Deployment](#backend-deployment)
4. [Desktop Applications](#desktop-applications)
5. [Payment Setup](#payment-setup)
6. [AI Configuration](#ai-configuration)
7. [Security Configuration](#security-configuration)
8. [Auto-updater Setup](#auto-updater-setup)
9. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

- **Python 3.9+** for backend
- **Node.js 18+** and **npm** for frontend applications
- **Rust** (latest stable) for Tauri desktop apps
- **PostgreSQL** database (Render provides this)
- **Redis** instance for rate limiting (optional)
- **Stripe Account** for payment processing
- **Claude API Account** for AI features
- **Email SMTP** service (Gmail, SendGrid, etc.)

## 🌍 Environment Setup

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd productivity-flow-saas
```

### 2. Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database

# Security Keys (Generate new ones for production!)
SECRET_KEY=your-super-secret-flask-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ENCRYPTION_KEY=your-fernet-encryption-key-here

# Stripe Configuration
STRIPE_SECRET_KEY=sk_live_... # Your Stripe secret key
STRIPE_PUBLISHABLE_KEY=pk_live_51RkaYhHHYuKoTuQQMGbXRhWQXBKR5JiFawdfBL7zrOHsay46EoEyYInWesRUUave2x68JY56lXFuYmFmREIHtLeP00YxMFIHTd

# Claude AI Configuration
CLAUDE_API_KEY=sk-ant-api03-your-actual-key-here
CLAUDE_API_KEY_ENCRYPTED=  # Leave empty for first run

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Frontend URL
FRONTEND_URL=https://your-frontend-domain.com

# Redis (Optional - for rate limiting)
REDIS_URL=redis://localhost:6379
```

### 3. Generate Security Keys

```python
# Run this Python script to generate secure keys
from cryptography.fernet import Fernet
import secrets

print("SECRET_KEY:", secrets.token_urlsafe(32))
print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
print("ENCRYPTION_KEY:", Fernet.generate_key().decode())
```

## 🚀 Backend Deployment

### Local Development

```bash
cd backend/
pip install -r requirements.txt
python application.py
```

### Render Deployment

1. **Create Render Account** at [render.com](https://render.com)

2. **Create PostgreSQL Database**:
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Choose a name (e.g., `productivityflow-db`)
   - Copy the connection string

3. **Create Web Service**:
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Select the `backend/` directory
   - Configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn application:application`
     - **Environment**: `Python 3`

4. **Add Environment Variables**:
   - Add all variables from your `.env` file
   - Use the PostgreSQL connection string as `DATABASE_URL`

5. **Deploy**: Click "Create Web Service"

## 💻 Desktop Applications

### Building Applications

#### Employee Tracker

```bash
cd employee-tracker-tauri/
npm install
npm run tauri build
```

#### Manager Dashboard

```bash
cd manager-dashboard-tauri/
npm install
npm run tauri build
```

### Build Output Locations

- **Windows**: `src-tauri/target/release/bundle/msi/`
- **Mac**: `src-tauri/target/release/bundle/dmg/`

### Cross-Platform Building

For Windows builds on Mac/Linux:
```bash
rustup target add x86_64-pc-windows-msvc
npm run tauri build -- --target x86_64-pc-windows-msvc
```

For Mac builds on Windows/Linux:
```bash
rustup target add x86_64-apple-darwin
npm run tauri build -- --target x86_64-apple-darwin
```

## 💳 Payment Setup

### 1. Stripe Configuration

1. **Create Stripe Account** at [stripe.com](https://stripe.com)
2. **Get API Keys**:
   - Go to Developers → API Keys
   - Copy Publishable and Secret keys
3. **Configure Webhooks**:
   - Go to Developers → Webhooks
   - Add endpoint: `https://your-backend-url.com/stripe/webhook`
   - Select events: `invoice.payment_succeeded`, `subscription.updated`

### 2. Pricing Setup

The system automatically charges **$9.99 per employee per month**:
- New employees are automatically added to billing
- Removing employees reduces the charge
- Billing is handled through Stripe subscriptions

### 3. Testing Payments

Use Stripe test cards:
- **Success**: `4242424242424242`
- **Decline**: `4000000000000002`

## 🤖 AI Configuration

### Claude API Setup

1. **Get Claude API Key**:
   - Visit [console.anthropic.com](https://console.anthropic.com)
   - Create account and get API key
   - Add your API key to environment variables: `CLAUDE_API_KEY=sk-ant-api03-your-actual-key-here`

2. **Token Limits**:
   - **Input**: ~2100 tokens per report
   - **Output**: ~200 tokens per report
   - **Cost Limit**: $2.00 per employee per day
   - **Model**: Claude 3 Haiku ($0.25/1M input, $1.25/1M output)

3. **Report Generation**:
   - Runs automatically every hour
   - Analyzes productivity patterns
   - Detects irregularities (auto-clickers, excessive idle time)
   - Stores reports for 1 week maximum

## 🔒 Security Configuration

### API Key Protection

- Claude API key is encrypted using Fernet encryption
- Stored in environment variables
- Never exposed in logs or client-side code

### Authentication

- JWT tokens with 7-day expiration
- bcrypt password hashing
- Rate limiting on all endpoints
- Email verification required

### Database Security

- SQL injection protection via SQLAlchemy ORM
- Connection pooling with encryption
- Indexed queries for performance

## 🔄 Auto-updater Setup

### Version Management

The auto-updater checks `/api/version` endpoint for:
- Current version number
- Download URLs for each platform
- Build dates

### Update Process

1. **Desktop apps check for updates** on startup
2. **Compare versions** with server
3. **Download new versions** if available
4. **Install and restart** automatically

### Deployment Workflow

1. **Build new versions** of desktop apps
2. **Upload to static hosting** (S3, CDN, etc.)
3. **Update version endpoint** with new URLs
4. **Apps auto-update** on next startup

## 🛠️ Troubleshooting

### Common Issues

#### Database Connection Errors
```bash
# Check DATABASE_URL format
postgresql://username:password@host:port/database

# Test connection
python -c "import psycopg2; psycopg2.connect('YOUR_DATABASE_URL')"
```

#### Stripe Webhook Issues
```bash
# Test webhook locally with Stripe CLI
stripe listen --forward-to localhost:5000/stripe/webhook
```

#### Claude API Errors
```bash
# Check API key and quota
curl -H "x-api-key: YOUR_API_KEY" https://api.anthropic.com/v1/messages
```

#### Email Sending Issues
```bash
# For Gmail, use App Passwords:
# 1. Enable 2FA on Google Account
# 2. Generate App Password
# 3. Use App Password as MAIL_PASSWORD
```

### Performance Optimization

#### Database Optimization
- Indexes are automatically created on frequently queried columns
- Connection pooling configured for high concurrency
- Old reports automatically cleaned up weekly

#### Token Usage Optimization
- Prompts limited to ~2100 input tokens
- Responses capped at 200 output tokens
- Daily spending limits enforced per employee

## 📞 Support

### Development Team Contact
- **Issues**: Create GitHub issues for bugs
- **Features**: Submit feature requests via GitHub
- **Security**: Email security issues privately

### Client Support
- **Setup Help**: Comprehensive documentation provided
- **Training**: Video tutorials for managers and employees
- **Billing**: Automatic Stripe billing support

## 📄 License

Proprietary software for ProductivityFlow SaaS platform.

---

**Ready to launch your productivity tracking SaaS!** 🚀

All systems are configured for scalability, security, and seamless user experience. The platform handles everything from user registration to automated billing and AI-powered insights.