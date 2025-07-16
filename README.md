# ProductivityFlow - Complete Development & Deployment Guide

![ProductivityFlow Logo](https://via.placeholder.com/400x100/4338ca/ffffff?text=ProductivityFlow)

## 🚀 Project Overview

ProductivityFlow is a comprehensive SaaS productivity tracking platform consisting of:

### Core Components
- **Flask Backend API** - Python-based REST API with PostgreSQL database
- **Employee Tracker Desktop App** - Tauri-based time tracking application 
- **Manager Dashboard Desktop App** - Tauri-based analytics and management interface

### Key Features
- **Real-time Time Tracking** with screenshot capture
- **AI-Powered Productivity Reports** using Claude AI
- **Team Management** with invite codes
- **Stripe Payment Integration** ($9.99/employee/month)
- **Auto-updater System** for seamless desktop app updates
- **Enhanced Security** with encrypted API key storage

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Testing with Developer Codes](#testing-with-developer-codes)
4. [Desktop Application Development](#desktop-application-development)
5. [Automated Build & Release](#automated-build--release)
6. [Production Deployment Steps](#production-deployment-steps)
7. [API Configuration](#api-configuration)
8. [Troubleshooting](#troubleshooting)

## 🔧 Prerequisites

Before starting development, ensure you have the following tools installed:

### Required Software
- **Python 3.9+** - For backend development
- **Node.js 18+** and **npm** - For frontend applications
- **Rust** (latest stable) - For Tauri desktop applications
- **Git** - For version control

### System Dependencies (Platform Specific)

#### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

#### Windows
```powershell
# Install Rust
# Download and run: https://forge.rust-lang.org/infra/rustup.html

# Install Visual Studio Build Tools
# Download and install Visual Studio Installer
# Install "C++ build tools" workload

# Install WebView2 (if not already installed)
# Usually comes with Windows 11, download for Windows 10
```

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt update
sudo apt install -y libwebkit2gtk-4.0-dev build-essential curl wget libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev

# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### Global Tools
```bash
# Install Tauri CLI globally
npm install -g @tauri-apps/cli@^1.5.0

# Verify installations
python --version    # Should be 3.9+
node --version      # Should be 18+
npm --version       # Should be 8+
rustc --version     # Should be latest stable
tauri --version     # Should be 1.5.x
```

## 🔧 Local Development Setup

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ProductivityFlow
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Set Up Environment Variables
Create a `.env` file in the `backend` directory:

```bash
# Backend Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-for-development
DATABASE_URL=postgresql://username:password@localhost:5432/productivityflow_dev

# Optional: For full feature testing
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
ANTHROPIC_API_KEY=your_claude_api_key
REDIS_URL=redis://localhost:6379

# Email Configuration (for notifications)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

#### Database Setup (Optional - Use Local PostgreSQL)
```bash
# Install PostgreSQL locally (optional - can use SQLite for development)
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create development database
createdb productivityflow_dev
```

#### Run the Backend
```bash
cd backend
python application.py
```

The backend will start on `http://localhost:5000`

### 3. Employee Tracker Desktop App

```bash
# Open a new terminal window/tab
cd employee-tracker-tauri

# Install dependencies
npm install

# Start in development mode
npm run tauri dev
```

The Employee Tracker app will launch automatically. It runs on port `1420` internally.

### 4. Manager Dashboard Desktop App

```bash
# Open another new terminal window/tab
cd manager-dashboard-tauri

# Install dependencies
npm install

# Start in development mode
npm run tauri dev
```

The Manager Dashboard app will launch automatically. It runs on port `1421` internally.

## 🧪 Testing with Developer Codes

The project includes pre-configured test teams for immediate testing without setting up payment systems.

### Available Test Teams

| Team | Employee Code | Description |
|------|---------------|-------------|
| Dev Team Alpha | `VMQDC2` | Primary development team |
| QA Test Team | `KX7T9U` | Quality assurance testing |
| Demo Team | `8945LG` | Product demonstrations |

### Testing Procedure

#### Employee App Testing
1. Launch the Employee Tracker app (`npm run tauri dev` in `employee-tracker-tauri/`)
2. Enter your name (any name for testing)
3. Use one of the employee codes above (e.g., `VMQDC2`)
4. Click "Join Team"
5. The app will start tracking your activity

#### Manager App Testing
1. Launch the Manager Dashboard app (`npm run tauri dev` in `manager-dashboard-tauri/`)
2. Enter your name (any name for testing)
3. Use the same team code as an employee
4. The app will show you as a manager if you're the first to join
5. View team analytics and employee activity

#### Backend API Testing
```bash
# Test backend health
curl http://localhost:5000/health

# Get all teams
curl http://localhost:5000/api/teams

# Join a team as employee
curl -X POST http://localhost:5000/api/teams/join \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Employee", "team_code": "VMQDC2"}'
```

## 📱 Desktop Application Development

### Development Commands

#### Employee Tracker
```bash
cd employee-tracker-tauri

# Development mode with hot reload
npm run tauri dev

# Build for production
npm run tauri build

# Build for specific platform
npm run tauri build -- --target universal-apple-darwin  # macOS universal
npm run tauri build -- --target x86_64-pc-windows-msvc   # Windows
```

#### Manager Dashboard
```bash
cd manager-dashboard-tauri

# Development mode with hot reload
npm run tauri dev

# Build for production
npm run tauri build

# Build for specific platform
npm run tauri build -- --target universal-apple-darwin  # macOS universal
npm run tauri build -- --target x86_64-pc-windows-msvc   # Windows
```

### Application Configuration

Both applications are configured to connect to:
- **Development**: `http://localhost:5000` (local backend)
- **Production**: `https://productivityflow-backend-v3.onrender.com`

To switch between environments, update the API base URL in the respective application's source code.

## 🚀 Automated Build & Release

### GitHub Actions Workflow

The project includes an automated build system that creates installers for both desktop applications.

#### How It Works
1. **Trigger**: Push a version tag (e.g., `git tag v1.0.0 && git push origin v1.0.0`)
2. **Build Matrix**: Parallel jobs build on macOS (for .dmg) and Windows (for .msi)
3. **Output**: GitHub Release with downloadable installers

#### Creating a Release
```bash
# Commit all changes
git add .
git commit -m "Release v1.0.0"

# Create and push tag
git tag v1.0.0
git push origin main
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build both apps for macOS and Windows
# 2. Create a GitHub Release
# 3. Upload installers as release assets
```

#### Release Assets
- `ProductivityFlow-Employee-Tracker-macOS.dmg`
- `ProductivityFlow-Employee-Tracker-Windows.msi`
- `ProductivityFlow-Manager-Dashboard-macOS.dmg`
- `ProductivityFlow-Manager-Dashboard-Windows.msi`

## 🌐 Production Deployment Steps

### Phase 1: Quick Testing (Current State)
The project is already configured for quick testing:

✅ **Backend**: Deployed on Render (`https://productivityflow-backend-v3.onrender.com`)  
✅ **Test Data**: Developer codes available for immediate testing  
✅ **Build System**: GitHub Actions ready for installer creation  

### Phase 2: Production Setup (Next Steps)

#### Backend Environment Variables (Render.com)
Configure these environment variables in your Render dashboard:

```bash
# Required for Production
SECRET_KEY=your-production-secret-key
DATABASE_URL=postgresql://username:password@host:port/database

# Payment Integration
STRIPE_SECRET_KEY=sk_live_your_live_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_live_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# AI Features
ANTHROPIC_API_KEY=your_claude_api_key

# Email Notifications
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your_sendgrid_api_key

# Redis (for rate limiting)
REDIS_URL=redis://username:password@host:port

# Security
FLASK_ENV=production
```

#### Database Migration
```bash
# If using a new production database, run migrations
cd backend
python -c "from application import app, db; app.app_context().push(); db.create_all()"
```

#### Stripe Webhook Setup
1. Log into Stripe Dashboard
2. Go to Developers > Webhooks
3. Add endpoint: `https://your-backend-url.onrender.com/stripe_webhook`
4. Select events: `checkout.session.completed`, `invoice.payment_succeeded`, `customer.subscription.updated`
5. Copy webhook secret to `STRIPE_WEBHOOK_SECRET` environment variable

#### Email Service Setup (SendGrid Example)
1. Create SendGrid account
2. Generate API key
3. Verify sender identity
4. Update email configuration in environment variables

### Phase 3: Desktop App Configuration

#### Update API Endpoints
Before building production installers, update the API base URL in both desktop applications:

1. **Employee Tracker**: Update API URL in `employee-tracker-tauri/src/`
2. **Manager Dashboard**: Update API URL in `manager-dashboard-tauri/src/`

#### Build Production Installers
```bash
# Tag and push for automated build
git tag v1.0.0
git push origin v1.0.0

# Or build locally
cd employee-tracker-tauri && npm run tauri build
cd manager-dashboard-tauri && npm run tauri build
```

## 🔑 API Configuration

### Required API Keys

#### Stripe (Payment Processing)
1. Create account at [stripe.com](https://stripe.com)
2. Get test keys for development
3. Get live keys for production
4. Set up webhook endpoints

#### Claude AI (Productivity Reports)
1. Create account at [anthropic.com](https://anthropic.com)
2. Generate API key
3. Add to environment variables

#### Email Service (Notifications)
Options:
- **SendGrid**: Professional email service
- **Gmail**: Use app passwords for development
- **AWS SES**: Scalable email service

### Environment Variables Reference

```bash
# Core Backend
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
FLASK_ENV=production

# Payment Processing
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# AI Integration
ANTHROPIC_API_KEY=your_claude_key

# Email Service
MAIL_SERVER=smtp.provider.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_username
MAIL_PASSWORD=your_password

# Caching & Rate Limiting
REDIS_URL=redis://host:port
```

## 🛠️ Troubleshooting

### Common Development Issues

#### Backend Won't Start
```bash
# Check Python version
python --version  # Must be 3.9+

# Install dependencies
pip install -r requirements.txt

# Check for missing environment variables
cd backend && python -c "from application import app"
```

#### Tauri Build Fails
```bash
# Update Rust
rustup update

# Clear cache and rebuild
npm run tauri build -- --debug

# Check system dependencies (Linux)
sudo apt install libwebkit2gtk-4.0-dev
```

#### Desktop App Can't Connect to Backend
1. Verify backend is running on `http://localhost:5000`
2. Check CORS configuration in `backend/application.py`
3. Verify API endpoints in desktop app source code

#### Database Connection Issues
```bash
# Check if PostgreSQL is running
pg_ctl status

# Verify database exists
psql -l | grep productivityflow

# Check connection string format
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### Production Issues

#### Render Deployment Fails
1. Check `runtime.txt` has correct Python version
2. Verify `requirements.txt` is complete
3. Check environment variables are set
4. Review Render logs for specific errors

#### Payment Integration Issues
1. Verify Stripe keys are correct environment (test vs live)
2. Check webhook endpoint is accessible
3. Verify webhook secret matches Stripe dashboard
4. Test with Stripe's test card numbers

#### Email Notifications Not Working
1. Verify SMTP credentials
2. Check if email service requires app passwords
3. Test SMTP connection manually
4. Verify sender email is verified with provider

### Getting Help

1. **Check Logs**: Always start with application logs
2. **Environment Variables**: Verify all required variables are set
3. **Dependencies**: Ensure all tools are latest compatible versions
4. **Documentation**: Reference official docs for Tauri, Flask, Stripe, etc.

---

## 📝 Developer Notes

- **Backend URL**: `https://productivityflow-backend-v3.onrender.com`
- **Test Codes**: See `DEVELOPER_CODES.md` for current test team codes
- **Build Artifacts**: Generated in `src-tauri/target/` directories
- **Log Files**: Check application logs for debugging information

**Last Updated**: December 2024