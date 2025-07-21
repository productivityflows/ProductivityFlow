#!/usr/bin/env python3
"""
Update API URLs in desktop apps after Railway deployment.
This script helps you quickly update all API endpoints to point to your new Railway backend.
"""

import os
import re
import sys

def update_file(file_path, old_url, new_url):
    """Update API URL in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count occurrences
        old_count = content.count(old_url)
        if old_count == 0:
            return False, 0
        
        # Replace URLs
        new_content = content.replace(old_url, new_url)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True, old_count
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False, 0

def main():
    print("🔄 API URL Update Script for Railway Migration")
    print("=" * 50)
    
    # Get the new Railway URL
    print("\n📝 Enter your new Railway backend URL:")
    print("Example: https://productivityflow-backend.railway.app")
    new_url = input("Railway URL: ").strip()
    
    if not new_url:
        print("❌ No URL provided. Exiting.")
        return
    
    if not new_url.startswith("https://"):
        print("❌ URL must start with https://")
        return
    
    # Old Render URL
    old_url = "https://my-home-backend-7m6d.onrender.com"
    
    # Files to update
    files_to_update = [
        # Employee Tracker
        "employee-tracker-tauri/src/components/OnboardingView.tsx",
        "employee-tracker-tauri/src/components/TrackingView.tsx",
        
        # Manager Dashboard
        "manager-dashboard-tauri/src/utils/api.ts",
        "manager-dashboard-tauri/src/pages/TeamManagement.tsx",
        
        # Web Dashboard
        "web-dashboard/src/pages/Dashboard.jsx",
        "web-dashboard/src/pages/TeamManagement.jsx",
        
        # Desktop Tracker
        "desktop-tracker/src/components/EmployeeTracker.jsx",
        "desktop-tracker/src/components/OnboardingView.jsx",
        
        # Backend scripts
        "backend/setup_dev_data.py",
    ]
    
    print(f"\n🔄 Updating API URLs from:")
    print(f"   Old: {old_url}")
    print(f"   New: {new_url}")
    print("\n" + "=" * 50)
    
    total_updated = 0
    total_files = 0
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            success, count = update_file(file_path, old_url, new_url)
            if success:
                print(f"✅ {file_path} - Updated {count} occurrences")
                total_updated += count
                total_files += 1
            else:
                print(f"⚠️  {file_path} - No changes needed")
        else:
            print(f"❌ {file_path} - File not found")
    
    print("\n" + "=" * 50)
    print(f"✅ Migration complete!")
    print(f"📊 Files updated: {total_files}")
    print(f"📊 Total URL replacements: {total_updated}")
    
    print(f"\n📋 Next steps:")
    print(f"1. Test your Railway backend: {new_url}/health")
    print(f"2. Build and test your desktop apps")
    print(f"3. Verify team creation and joining works")
    
    # Save the new URL for reference
    with open("railway_backend_url.txt", "w") as f:
        f.write(f"Railway Backend URL: {new_url}\n")
        f.write(f"Updated on: {__import__('datetime').datetime.now()}\n")
    
    print(f"\n💾 Railway URL saved to: railway_backend_url.txt")

if __name__ == "__main__":
    main() 