# Backend Deployment Guide for Render

## Pre-Deployment Checklist

### 1. Verify Backend Changes
The backend has been updated with the following critical fixes:
- ✅ Added missing API endpoints (`/api/teams/public`, `/api/teams/<id>/members`)
- ✅ Enhanced CORS configuration for Tauri applications
- ✅ Enabled rate limiting by default
- ✅ Improved encryption key handling
- ✅ Fixed API response formats

### 2. Required Environment Variables for Render

Set these environment variables in your Render dashboard:

#### Essential Variables
```bash
# Database (Auto-configured by Render PostgreSQL)
DATABASE_URL=postgresql://...  # Render provides this automatically

# Security (Generate these)
SECRET_KEY=your-flask-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# Production Settings
FLASK_ENV=production
ENABLE_RATE_LIMITING=true
```

#### Optional Variables
```bash
# Email (if using email features)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@domain.com

# Stripe (if using payment features)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Claude AI (if using AI features)
CLAUDE_API_KEY=your-claude-api-key

# Redis (if available)
REDIS_URL=redis://...
```

### 3. Generate Encryption Key

Run this locally to generate a secure encryption key:

```bash
cd backend
python generate_encryption_key.py
```

Copy the output and set it as the `ENCRYPTION_KEY` environment variable in Render.

## Deployment Steps

### 1. Push Changes to Repository

Ensure your repository includes all the backend fixes:

```bash
git add .
git commit -m "Fix: Backend API endpoints and frontend communication"
git push origin main
```

### 2. Deploy on Render

1. **Login to Render**: Go to https://render.com
2. **Select Web Service**: Choose your existing backend service
3. **Manual Deploy**: Click "Manual Deploy" to deploy latest changes
4. **Set Environment Variables**: In Settings → Environment, add all required variables
5. **Health Check**: Verify the service starts successfully

### 3. Verify Deployment

Test these endpoints after deployment:

#### Health Check
```bash
curl https://productivityflow-backend-v3.onrender.com/api/version
```

Expected response:
```json
{
  "version": "1.0.0",
  "build_date": "2024-01-15",
  "download_urls": { ... }
}
```

#### Test Team Creation
```bash
curl -X POST https://productivityflow-backend-v3.onrender.com/api/teams \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Team", "user_name": "Test Manager", "role": "manager"}'
```

Expected response:
```json
{
  "message": "Team created successfully",
  "token": "...",
  "team": {
    "id": "team_...",
    "name": "Test Team",
    "employee_code": "ABC123"
  },
  "user": { ... }
}
```

#### Test Public Teams
```bash
curl https://productivityflow-backend-v3.onrender.com/api/teams/public
```

Expected response:
```json
{
  "teams": [
    {
      "id": "team_...",
      "name": "Test Team",
      "code": "ABC123",
      "memberCount": 1
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. 404 Errors
- **Cause**: Backend not deployed or wrong URL
- **Solution**: Verify deployment status in Render dashboard
- **Check**: Service logs for startup errors

#### 2. CORS Errors
- **Cause**: Missing CORS headers
- **Solution**: Verify CORS configuration in application.py
- **Check**: Browser developer tools for specific errors

#### 3. Database Errors
- **Cause**: Missing DATABASE_URL or connection issues
- **Solution**: Verify PostgreSQL service is connected
- **Check**: Database connection logs

#### 4. Rate Limiting Issues
- **Cause**: Too many requests from same IP
- **Solution**: Temporarily disable with `ENABLE_RATE_LIMITING=false`
- **Check**: Backend logs for rate limit messages

### Debug Commands

#### Check Service Status
```bash
curl -I https://productivityflow-backend-v3.onrender.com/
```

#### View Error Response
```bash
curl -v https://productivityflow-backend-v3.onrender.com/api/teams/public
```

#### Test CORS
```bash
curl -X OPTIONS https://productivityflow-backend-v3.onrender.com/api/teams \
  -H "Origin: tauri://localhost" \
  -H "Access-Control-Request-Method: POST"
```

## Post-Deployment Testing

### 1. Manager Dashboard Test
1. Open the manager dashboard Tauri app
2. Create a new team: "Production Test Team"
3. Verify you receive a team code
4. Check that the team appears in the teams list

### 2. Employee Tracker Test
1. Open the employee tracker Tauri app
2. Enter name: "Test Employee"
3. Enter the team code from step 1
4. Click "Join Team"
5. Verify successful connection

### 3. Full Integration Test
1. Create multiple teams from the manager dashboard
2. Join teams from multiple employee trackers
3. Verify all data appears correctly
4. Test error scenarios (wrong team codes, etc.)

## Performance Optimization

### Database Connection Pooling
The application is configured with optimized connection pooling:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pool timeout: 20 seconds
- Connection recycling: 300 seconds

### Rate Limiting
Default limits are conservative for stability:
- 1000 requests per hour per IP
- 200 requests per minute per IP

Adjust these in the backend code if needed for your usage patterns.

## Security Checklist

- ✅ ENCRYPTION_KEY set to secure value
- ✅ SECRET_KEY set to secure value  
- ✅ JWT_SECRET_KEY set to secure value
- ✅ Rate limiting enabled
- ✅ CORS properly configured for Tauri
- ✅ Database connection secured
- ✅ No sensitive data in logs

## Support

If deployment fails, check:
1. Render service logs
2. Environment variable configuration
3. Database connection status
4. GitHub repository sync status

The system should be fully functional after following this deployment guide.