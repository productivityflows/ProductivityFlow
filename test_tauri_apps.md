# Tauri Applications Testing Guide

## Building and Testing the Fixed Applications

### Prerequisites
Ensure you have the latest code with all fixes applied:
```bash
git pull origin main
```

### Manager Dashboard Tauri App

#### Build the Application
```bash
cd manager-dashboard-tauri
npm install
npm run tauri build
```

#### Test Team Creation
1. **Launch the app**: Run the built executable or use `npm run tauri dev`
2. **Navigate to Team Management**: Click on "Team Management" in the sidebar
3. **Create a team**:
   - Enter team name: "Test Production Team"
   - Click "Create Team" button
   - **Expected**: Success alert with team code (e.g., "ABC123")
   - **Expected**: Team appears in the teams list
4. **Verify team details**:
   - Click on the created team
   - **Expected**: Team code is displayed
   - **Expected**: Copy button works for the team code

#### Debug Mode Testing
```bash
cd manager-dashboard-tauri
npm run tauri dev
```
- Open browser developer tools (F12)
- Check Console tab for any errors
- Check Network tab to verify API calls to correct URL

### Employee Tracker Tauri App

#### Build the Application
```bash
cd employee-tracker-tauri
npm install
npm run tauri build
```

#### Test Team Joining
1. **Launch the app**: Run the built executable or use `npm run tauri dev`
2. **Join team**:
   - Enter name: "Test Employee"
   - Enter team code from manager dashboard test
   - Click "Join Team" button
   - **Expected**: Successful login to tracking interface
3. **Verify session**:
   - **Expected**: Team name displayed in header
   - **Expected**: User name displayed correctly
   - **Expected**: No error messages

#### Debug Mode Testing
```bash
cd employee-tracker-tauri
npm run tauri dev
```
- Open browser developer tools (F12)
- Check Console tab for API communication logs
- Verify successful team join response

## Expected API Communication

### Manager Dashboard → Backend
```
POST https://productivityflow-backend-v3.onrender.com/api/teams
Content-Type: application/json

{
  "name": "Test Production Team",
  "user_name": "Manager",
  "role": "manager"
}
```

**Expected Response:**
```json
{
  "message": "Team created successfully",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "team": {
    "id": "team_abc123def456",
    "name": "Test Production Team",
    "employee_code": "ABC123"
  },
  "user": {
    "id": "user_def456ghi789",
    "name": "Manager",
    "role": "manager"
  }
}
```

### Employee Tracker → Backend
```
POST https://productivityflow-backend-v3.onrender.com/api/teams/join
Content-Type: application/json

{
  "employee_name": "Test Employee",
  "team_code": "ABC123"
}
```

**Expected Response:**
```json
{
  "success": true,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "emp_abc12345",
    "name": "Test Employee",
    "role": "employee"
  },
  "team": {
    "id": "team_abc123def456",
    "name": "Test Production Team",
    "code": "ABC123"
  }
}
```

## Troubleshooting Common Issues

### 1. API Connection Errors
**Symptoms**: 
- "Cannot connect to server" errors
- Network request failures
- Timeout errors

**Solutions**:
1. Verify backend is deployed and accessible
2. Check API URL in source files matches deployed backend
3. Test backend endpoints manually with curl
4. Check CORS configuration

### 2. Team Creation Failures
**Symptoms**:
- "Create Team" button does nothing
- Error messages about missing fields
- HTTP 400/500 errors

**Solutions**:
1. Check request payload format matches backend expectations
2. Verify all required fields are included
3. Check backend logs for specific error messages
4. Test API endpoint directly with curl

### 3. Team Joining Failures
**Symptoms**:
- "Invalid team code" errors
- "Team code not found" errors
- Login failures

**Solutions**:
1. Verify team code was created correctly
2. Check field name in request (`employee_name` not `name`)
3. Ensure team code is uppercase
4. Test join endpoint directly with curl

### 4. UI/UX Issues
**Symptoms**:
- Buttons not responding
- Loading states stuck
- Missing error messages

**Solutions**:
1. Check browser console for JavaScript errors
2. Verify state management in React components
3. Add console.log statements for debugging
4. Test in both dev and production modes

## Performance Testing

### Load Testing Team Creation
```bash
# Test multiple team creations
for i in {1..5}; do
  curl -X POST https://productivityflow-backend-v3.onrender.com/api/teams \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"Test Team $i\", \"user_name\": \"Manager $i\", \"role\": \"manager\"}"
  echo ""
done
```

### Load Testing Team Joining
```bash
# Test multiple team joins (use actual team codes)
for i in {1..5}; do
  curl -X POST https://productivityflow-backend-v3.onrender.com/api/teams/join \
    -H "Content-Type: application/json" \
    -d "{\"employee_name\": \"Employee $i\", \"team_code\": \"ABC123\"}"
  echo ""
done
```

## Success Criteria

✅ **Manager Dashboard**:
- Team creation works without errors
- Team code is generated and displayed
- Team appears in teams list
- UI is responsive and user-friendly

✅ **Employee Tracker**:
- Team joining works with valid codes
- Error handling for invalid codes
- Successful transition to tracking interface
- Session persistence

✅ **Backend Communication**:
- All API calls use correct URL
- Request/response formats match
- CORS headers allow Tauri requests
- Rate limiting doesn't block normal usage

✅ **Error Handling**:
- Clear error messages for users
- Proper HTTP status codes
- Graceful failure scenarios
- Detailed logging for debugging

## Final Validation

After all tests pass:
1. **Production Build**: Create production builds of both Tauri apps
2. **Cross-Platform**: Test on different operating systems if possible
3. **End-to-End**: Complete workflow from team creation to joining
4. **Documentation**: Update user documentation with any changes
5. **Deployment**: Prepare for distribution of fixed applications

The system should now be fully functional with proper communication between the Tauri desktop applications and the live backend server.