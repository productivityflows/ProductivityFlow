# ProductivityFlow Desktop Apps Setup Guide

This guide will help you set up and run the complete ProductivityFlow system with two Tauri desktop applications: one for employees (tracker) and one for managers (dashboard).

## 🎯 Project Overview

**New Architecture:**
- **Backend**: Enhanced Flask API with role-based authentication (deployed on Render)
- **Employee Tracker**: Tauri desktop app with real system monitoring
- **Manager Dashboard**: Tauri desktop app for team analytics
- **Database**: PostgreSQL (hosted on Render)

## 🧪 Developer Test Codes

**For quick testing and development, we have pre-generated test teams with known codes:**

- **Dev Team Alpha**: Employee Code `VMQDC2`
- **QA Test Team**: Employee Code `KX7T9U`  
- **Demo Team**: Employee Code `8945LG`

📋 **View all codes**: `cat DEVELOPER_CODES.md`
🔄 **Generate new codes**: `./generate_dev_codes.sh`

These codes allow you to immediately test both the Employee Tracker and Manager Dashboard apps without needing to create teams manually.

## 📋 Prerequisites

### System Requirements
- **Node.js**: v18 or higher
- **Rust**: Latest stable version
- **Python**: 3.9+ (for backend development)
- **Platform**: Windows, macOS, or Linux

### Install Required Tools

1. **Install Node.js**: Download from [nodejs.org](https://nodejs.org/)

2. **Install Rust**: 
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source ~/.cargo/env
   ```

3. **Install Tauri CLI**:
   ```bash
   npm install -g @tauri-apps/cli
   ```

4. **Platform-specific dependencies**:
   
   **macOS:**
   ```bash
   xcode-select --install
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install libwebkit2gtk-4.0-dev \
       build-essential \
       curl \
       wget \
       libssl-dev \
       libgtk-3-dev \
       libayatana-appindicator3-dev \
       librsvg2-dev \
       libx11-dev \
       libxss-dev
   ```
   
   **Windows:**
   - Install Visual Studio Build Tools or Visual Studio Community
   - Install WebView2 (usually pre-installed on Windows 11)

## 🚀 Setup Instructions

### Step 1: Backend Setup (Already Deployed)

The backend is already deployed on Render at:
- **URL**: `https://productivityflow-backend-v3.onrender.com`
- **Database**: PostgreSQL (hosted on Render)

**Key Features Added:**
- Role-based authentication with JWT tokens
- Separate employee codes and manager invite codes
- Rate limiting for security
- Enhanced activity tracking with app names and window titles
- Scalability improvements for 10,000+ users

### Step 2: Employee Tracker Setup

1. **Navigate to the employee tracker directory**:
   ```bash
   cd employee-tracker-tauri
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Development mode**:
   ```bash
   npm run tauri dev
   ```

4. **Build for production**:
   ```bash
   npm run tauri build
   ```

**Features:**
- Real-time desktop activity monitoring
- System tray integration
- Active window tracking
- Idle time detection
- Secure authentication with employee codes

### Step 3: Manager Dashboard Setup

1. **Navigate to the manager dashboard directory**:
   ```bash
   cd manager-dashboard-tauri
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Add the React components** (copy from web-dashboard/src):
   ```bash
   # Copy the existing dashboard components
   cp -r ../web-dashboard/src/components ./src/
   cp -r ../web-dashboard/src/pages ./src/
   ```

4. **Create the main App.tsx**:
   ```typescript
   // You'll need to adapt the web-dashboard App.jsx to TypeScript
   // and integrate with Tauri APIs for the manager login flow
   ```

5. **Development mode**:
   ```bash
   npm run tauri dev
   ```

6. **Build for production**:
   ```bash
   npm run tauri build
   ```

## 🔐 Authentication Flow

### Employee Flow
1. Employee receives a **6-character Employee Code** from their manager
2. Downloads and installs the Employee Tracker app
3. Enters name + employee code to join team
4. App starts tracking activity automatically

### Manager Flow
1. Manager creates a team (generates both employee code and manager invite code)
2. Downloads and installs the Manager Dashboard app
3. Uses the **12-character Manager Invite Code** to claim manager role
4. Can view team analytics, member activity, and manage tasks

## 🗄️ Database Schema Updates

**New/Updated Tables:**
- `teams`: Added `employee_code` field, separated from manager access
- `manager_invites`: New table for secure manager role assignment
- `memberships`: Enhanced with role field and timestamps
- `activities`: Added `active_app`, `window_title`, `idle_time` fields
- `user_sessions`: Added role tracking and JWT token hashing

## 🏃‍♂️ How to Run the Complete System

### 1. Create a Team (Manager)
```bash
# The manager creates a team via the API or frontend
curl -X POST https://productivityflow-backend-v3.onrender.com/api/teams \
  -H "Content-Type: application/json" \
  -d '{"name": "Development Team"}'

# Response includes:
# - employee_code: "ABC123" (for employees)
# - manager_invite_code: "XyZ9k2M8nQ4p" (for manager, one-time use)
```

### 2. Manager Claims Role
1. Manager installs Manager Dashboard app
2. Uses the manager invite code to claim role
3. Gets manager-level access with JWT token

### 3. Employees Join
1. Employees install Employee Tracker app
2. Use the employee code to join team
3. Start activity tracking

### 4. Real-time Tracking
- Employee apps monitor desktop activity every 30 seconds
- Data is sent to backend with proper authentication
- Manager can view real-time analytics

## 🔧 Development Tips

### Debugging the Employee Tracker
1. **Check system permissions**: The app needs accessibility permissions on macOS
2. **Console output**: Use `console.log` in React and `println!` in Rust
3. **Network issues**: Verify the backend URL is accessible

### Debugging the Manager Dashboard
1. **API authentication**: Ensure JWT tokens are properly included in requests
2. **CORS issues**: Backend is configured for cross-origin requests
3. **Component loading**: Verify all dashboard components are properly migrated

### Common Issues

**Rust compilation errors:**
```bash
# Clean and rebuild
cd employee-tracker-tauri
cargo clean
npm run tauri build
```

**Permission errors on macOS:**
- Grant accessibility permissions in System Preferences > Security & Privacy

**Network connectivity:**
```bash
# Test backend connectivity
curl https://productivityflow-backend-v3.onrender.com/health
```

## 📱 Platform-Specific Notes

### macOS
- Requires accessibility permissions for window tracking
- Apps can be signed for distribution
- System tray integration works seamlessly

### Windows
- Requires Visual Studio Build Tools
- WebView2 dependency (usually pre-installed)
- UAC permissions may be needed for system monitoring

### Linux
- Requires X11 libraries for window tracking
- AppImage format for easy distribution
- System tray support varies by desktop environment

## 🔒 Security Considerations

1. **JWT Tokens**: 7-day expiration, stored securely
2. **Rate Limiting**: API endpoints are rate-limited
3. **Role Separation**: Employees cannot access manager data
4. **Code Expiration**: Manager invite codes expire after 30 days
5. **HTTPS Only**: All communication is encrypted

## 📈 Scalability Features

- Connection pooling for database
- Redis support for session storage
- Rate limiting with Redis backend
- Indexed database queries
- JWT-based stateless authentication

## 🛠️ Building for Distribution

### Employee Tracker
```bash
cd employee-tracker-tauri
npm run tauri build
# Outputs: src-tauri/target/release/bundle/
```

### Manager Dashboard
```bash
cd manager-dashboard-tauri
npm run tauri build
# Outputs: src-tauri/target/release/bundle/
```

**Distribution formats:**
- **Windows**: `.exe` installer, `.msi` package
- **macOS**: `.app` bundle, `.dmg` image
- **Linux**: `.deb`, `.rpm`, `.AppImage`

## 🚨 Troubleshooting

### Backend Issues
- Check Render deployment logs
- Verify DATABASE_URL environment variable
- Test health endpoint: `/health`

### Desktop App Issues
- Verify Rust/Node.js versions
- Check platform-specific dependencies
- Review Tauri configuration

### Authentication Issues
- Verify team codes are correct
- Check JWT token validity
- Ensure proper API endpoints

## 📞 Support

For issues or questions:
1. Check the console logs in both React and Rust
2. Verify network connectivity to the backend
3. Ensure all dependencies are properly installed
4. Check platform-specific permission requirements

---

**🎉 You now have a complete desktop productivity tracking system with:**
- Real system monitoring for employees
- Comprehensive dashboard for managers  
- Secure role-based authentication
- Scalable backend architecture
- Cross-platform desktop applications