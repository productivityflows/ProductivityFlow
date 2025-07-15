#!/usr/bin/env python3
"""
ProductivityFlow - Developer Test Credentials Setup
This script creates test teams and credentials for development testing.
"""

import requests
import json
import random
import string
from datetime import datetime, timedelta

# Configuration
API_BASE_URL = "https://productivityflow-backend-v3.onrender.com"

def generate_random_string(length=8):
    """Generate a random string for test data"""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def create_test_team():
    """Create a test team and return team details"""
    team_name = f"Dev Test Team {generate_random_string(4)}"
    
    print(f"🏢 Creating test team: {team_name}")
    
    response = requests.post(f"{API_BASE_URL}/api/teams", json={
        "name": team_name
    })
    
    if response.status_code == 200:
        team_data = response.json()
        print(f"✅ Team created successfully!")
        print(f"   Team ID: {team_data['id']}")
        print(f"   Team Name: {team_data['name']}")
        print(f"   Employee Code: {team_data['employee_code']}")
        print(f"   Manager Invite Code: {team_data['manager_invite_code']}")
        return team_data
    else:
        print(f"❌ Failed to create team: {response.text}")
        return None

def join_as_employee(team_code, employee_name):
    """Join team as an employee"""
    print(f"👤 Joining as employee: {employee_name}")
    
    response = requests.post(f"{API_BASE_URL}/api/teams/join", json={
        "name": employee_name,
        "team_code": team_code
    })
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Employee joined successfully!")
        print(f"   User ID: {user_data['userId']}")
        print(f"   Username: {user_data['userName']}")
        print(f"   Role: {user_data['role']}")
        print(f"   Token: {user_data['token'][:50]}...")
        return user_data
    else:
        print(f"❌ Failed to join as employee: {response.text}")
        return None

def claim_manager_role(manager_invite_code, manager_name):
    """Claim manager role"""
    print(f"👑 Claiming manager role: {manager_name}")
    
    response = requests.post(f"{API_BASE_URL}/api/teams/claim-manager-role", json={
        "name": manager_name,
        "manager_invite_code": manager_invite_code
    })
    
    if response.status_code == 200:
        manager_data = response.json()
        print(f"✅ Manager role claimed successfully!")
        print(f"   User ID: {manager_data['userId']}")
        print(f"   Username: {manager_data['userName']}")
        print(f"   Role: {manager_data['role']}")
        print(f"   Token: {manager_data['token'][:50]}...")
        return manager_data
    else:
        print(f"❌ Failed to claim manager role: {response.text}")
        return None

def add_sample_data(team_id, token):
    """Add sample productivity data"""
    print(f"📊 Adding sample data to team...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE_URL}/api/teams/{team_id}/sample-data", headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Sample data added successfully!")
    else:
        print(f"❌ Failed to add sample data: {response.text}")

def main():
    print("🚀 ProductivityFlow Developer Test Setup")
    print("=" * 50)
    
    # Create test team
    team_data = create_test_team()
    if not team_data:
        return
    
    print("\n" + "=" * 50)
    
    # Create test employees
    employees = []
    employee_names = [
        "John Doe (Dev Employee)",
        "Jane Smith (Dev Employee)", 
        "Mike Johnson (Dev Employee)"
    ]
    
    for name in employee_names:
        employee_data = join_as_employee(team_data['employee_code'], name)
        if employee_data:
            employees.append(employee_data)
    
    print("\n" + "=" * 50)
    
    # Create test manager
    manager_data = claim_manager_role(team_data['manager_invite_code'], "Alex Manager (Dev Manager)")
    
    if manager_data:
        print("\n" + "=" * 50)
        # Add sample data
        add_sample_data(team_data['id'], manager_data['token'])
    
    print("\n" + "🎉 TEST SETUP COMPLETE!")
    print("=" * 50)
    
    # Print summary for easy copying
    print("\n📋 DEVELOPER CREDENTIALS SUMMARY:")
    print("-" * 40)
    print(f"Team Name: {team_data['name']}")
    print(f"Team ID: {team_data['id']}")
    print(f"Employee Code: {team_data['employee_code']}")
    print(f"Manager Invite Code: {team_data['manager_invite_code']}")
    
    print("\n👥 EMPLOYEE TEST ACCOUNTS:")
    for i, emp in enumerate(employees, 1):
        print(f"  Employee {i}: {emp['userName']}")
        print(f"    User ID: {emp['userId']}")
        print(f"    Token: {emp['token']}")
    
    if manager_data:
        print(f"\n👑 MANAGER TEST ACCOUNT:")
        print(f"  Manager: {manager_data['userName']}")
        print(f"    User ID: {manager_data['userId']}")
        print(f"    Token: {manager_data['token']}")
    
    print("\n📱 TESTING INSTRUCTIONS:")
    print("-" * 40)
    print("1. Employee Tracker Testing:")
    print(f"   - Use Employee Code: {team_data['employee_code']}")
    print("   - Enter any name (e.g., 'Test Employee')")
    print("   - The app will create a new employee or login existing")
    
    print("\n2. Manager Dashboard Testing:")
    print(f"   - Use Manager Invite Code: {team_data['manager_invite_code']}")
    print("   - Enter any name (e.g., 'Test Manager')")
    print("   - You'll get manager access to view team data")
    
    print("\n3. API Testing:")
    print("   - Use the tokens above for API authentication")
    print("   - Add 'Bearer <token>' to Authorization header")
    
    print("\n💡 NOTE: These are test credentials for development only!")

if __name__ == "__main__":
    main()