# Developer Test Codes

Generated on: 2025-07-15 17:36:14

## Backend URL
```
https://productivityflow-backend-v3.onrender.com
```

## Test Teams

### 1. Dev Team Alpha
**Team ID**: `team_1752600970_3hsj8bt6`
**Employee Code**: `VMQDC2`
**Manager Invite Code**: `Not available (old API)`
**Description**: Primary development team for testing

---

### 2. QA Test Team
**Team ID**: `team_1752600970_4cyq3b7b`
**Employee Code**: `KX7T9U`
**Manager Invite Code**: `Not available (old API)`
**Description**: Quality assurance team for testing

---

### 3. Demo Team
**Team ID**: `team_1752600970_59ucxcaj`
**Employee Code**: `8945LG`
**Manager Invite Code**: `Not available (old API)`
**Description**: Team for product demonstrations

---

## How to Test

### Employee App Testing
1. Open the Employee Tracker app
2. Use any of the **Employee Codes** above
3. Enter your name and the code to join a team
4. The app will start tracking your activity

### Manager App Testing  
1. Open the Manager Dashboard app
2. Use any of the **Manager Invite Codes** above (if available)
3. Enter your name and the code to claim manager role
4. View team analytics and manage employees

### API Testing
```bash
# Test backend health
curl https://productivityflow-backend-v3.onrender.com/health

# Get all teams
curl https://productivityflow-backend-v3.onrender.com/api/teams

# Join a team as employee
curl -X POST https://productivityflow-backend-v3.onrender.com/api/teams/join \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Employee", "team_code": "EMPLOYEE_CODE_HERE"}'
```

## Quick Test Codes

Here are the codes you can use immediately:

**Dev Team Alpha**
- Employee: `VMQDC2`
- Manager: `Not available`

**QA Test Team**
- Employee: `KX7T9U`
- Manager: `Not available`

**Demo Team**
- Employee: `8945LG`
- Manager: `Not available`


## Notes
- Employee codes are 6 characters long
- Manager invite codes are 12 characters long (if available)
- Manager codes can only be used once
- Employee codes can be used multiple times
- All test data is temporary and can be recreated by running this script again
- If manager codes show "Not available", you're using an older API version
