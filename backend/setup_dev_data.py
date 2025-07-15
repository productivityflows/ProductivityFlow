#!/usr/bin/env python3
"""
Developer Setup Script
Creates test teams with known codes for easy testing
"""
import os
import sys
import requests
import json
from datetime import datetime

# Backend URL - update this if different
BACKEND_URL = os.environ.get('BACKEND_URL', 'https://productivityflow-backend-v3.onrender.com')

def create_test_teams():
    """Create test teams with known codes for developers"""
    
    teams_to_create = [
        {
            "name": "Dev Team Alpha",
            "description": "Primary development team for testing"
        },
        {
            "name": "QA Test Team",
            "description": "Quality assurance team for testing"
        },
        {
            "name": "Demo Team",
            "description": "Team for product demonstrations"
        }
    ]
    
    created_teams = []
    
    for team_data in teams_to_create:
        try:
            # Create team
            response = requests.post(f"{BACKEND_URL}/api/teams", 
                                   json={"name": team_data["name"]},
                                   headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                team_info = response.json()
                team_info["description"] = team_data["description"]
                
                # Handle both old and new API formats
                if 'code' in team_info and 'employee_code' not in team_info:
                    team_info['employee_code'] = team_info['code']
                
                # Check if manager_invite_code is missing (old API)
                if 'manager_invite_code' not in team_info:
                    team_info['manager_invite_code'] = 'NOT_AVAILABLE_IN_OLD_API'
                
                created_teams.append(team_info)
                print(f"✅ Created team: {team_info['name']}")
                print(f"   Employee Code: {team_info.get('employee_code', team_info.get('code', 'N/A'))}")
                
                if team_info.get('manager_invite_code', '') != 'NOT_AVAILABLE_IN_OLD_API':
                    print(f"   Manager Code: {team_info.get('manager_invite_code', 'N/A')}")
                else:
                    print(f"   Manager Code: Not available (old API version)")
                print()
            else:
                print(f"❌ Failed to create team {team_data['name']}: {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating team {team_data['name']}: {e}")
    
    return created_teams

def create_sample_users(teams):
    """Create sample users for each team"""
    
    sample_employees = [
        "Alice Johnson",
        "Bob Smith", 
        "Carol Davis",
        "David Wilson"
    ]
    
    sample_managers = [
        "Manager Sarah",
        "Manager Mike",
        "Manager Lisa"
    ]
    
    print("Creating sample users...")
    
    for i, team in enumerate(teams):
        try:
            # Only create manager if we have a valid manager invite code
            manager_code = team.get('manager_invite_code')
            if i < len(sample_managers) and manager_code and manager_code != 'NOT_AVAILABLE_IN_OLD_API':
                manager_data = {
                    "name": sample_managers[i],
                    "manager_invite_code": manager_code
                }
                
                response = requests.post(f"{BACKEND_URL}/api/teams/claim-manager-role",
                                       json=manager_data,
                                       headers={"Content-Type": "application/json"})
                
                if response.status_code == 200:
                    print(f"✅ Created manager: {sample_managers[i]} for {team['name']}")
                else:
                    print(f"❌ Failed to create manager for {team['name']}: {response.text}")
            elif manager_code == 'NOT_AVAILABLE_IN_OLD_API':
                print(f"⚠️  Skipping manager creation for {team['name']} (old API version)")
            
            # Create employees for this team
            employee_code = team.get('employee_code', team.get('code'))
            if employee_code:
                for j, emp_name in enumerate(sample_employees):
                    if j <= i:  # Different number of employees per team
                        employee_data = {
                            "name": emp_name,
                            "team_code": employee_code
                        }
                        
                        response = requests.post(f"{BACKEND_URL}/api/teams/join",
                                               json=employee_data,
                                               headers={"Content-Type": "application/json"})
                        
                        if response.status_code == 200:
                            print(f"✅ Created employee: {emp_name} for {team['name']}")
                        else:
                            print(f"❌ Failed to create employee {emp_name}: {response.text}")
            else:
                print(f"❌ No employee code found for team {team['name']}")
                        
        except Exception as e:
            print(f"❌ Error creating users for {team['name']}: {e}")

def generate_markdown_summary(teams):
    """Generate a markdown file with all the developer codes"""
    
    markdown_content = f"""# Developer Test Codes

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Backend URL
```
{BACKEND_URL}
```

## Test Teams

"""
    
    for i, team in enumerate(teams, 1):
        employee_code = team.get('employee_code', team.get('code', 'N/A'))
        manager_code = team.get('manager_invite_code', 'N/A')
        
        markdown_content += f"""### {i}. {team['name']}
**Team ID**: `{team.get('id', 'N/A')}`
**Employee Code**: `{employee_code}`
**Manager Invite Code**: `{manager_code if manager_code != 'NOT_AVAILABLE_IN_OLD_API' else 'Not available (old API)'}`
**Description**: {team.get('description', 'Test team')}

---

"""
    
    markdown_content += f"""## How to Test

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
curl {BACKEND_URL}/health

# Get all teams
curl {BACKEND_URL}/api/teams

# Join a team as employee
curl -X POST {BACKEND_URL}/api/teams/join \\
  -H "Content-Type: application/json" \\
  -d '{{"name": "Test Employee", "team_code": "EMPLOYEE_CODE_HERE"}}'
```

## Quick Test Codes

Here are the codes you can use immediately:

"""
    
    # Add a quick reference section
    for i, team in enumerate(teams, 1):
        employee_code = team.get('employee_code', team.get('code', 'N/A'))
        manager_code = team.get('manager_invite_code', 'N/A')
        
        markdown_content += f"""**{team['name']}**
- Employee: `{employee_code}`
- Manager: `{manager_code if manager_code != 'NOT_AVAILABLE_IN_OLD_API' else 'Not available'}`

"""

    markdown_content += """
## Notes
- Employee codes are 6 characters long
- Manager invite codes are 12 characters long (if available)
- Manager codes can only be used once
- Employee codes can be used multiple times
- All test data is temporary and can be recreated by running this script again
- If manager codes show "Not available", you're using an older API version
"""
    
    return markdown_content

def main():
    print("🚀 Setting up developer test data...")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Test backend connectivity
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            print("✅ Backend is accessible")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return
    
    print()
    
    # Create test teams
    teams = create_test_teams()
    
    if not teams:
        print("❌ No teams were created successfully")
        return
    
    print()
    
    # Create sample users
    create_sample_users(teams)
    
    print()
    
    # Generate summary
    markdown_content = generate_markdown_summary(teams)
    
    # Write to file
    with open('DEVELOPER_CODES.md', 'w') as f:
        f.write(markdown_content)
    
    print("✅ Developer codes saved to DEVELOPER_CODES.md")
    print()
    print("🎉 Setup complete! You can now test the applications using the codes in DEVELOPER_CODES.md")

if __name__ == "__main__":
    main()