#!/usr/bin/env python3
"""
Generate environment variables for Railway deployment.
This script creates secure keys and provides the exact values to copy into Railway.
"""

import secrets
import string
from cryptography.fernet import Fernet

def generate_secret_key(length=32):
    """Generate a secure secret key."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=64):
    """Generate a secure JWT secret key."""
    return secrets.token_urlsafe(length)

def generate_encryption_key():
    """Generate a Fernet encryption key."""
    return Fernet.generate_key().decode()

def main():
    print("🔐 Generating Environment Variables for Railway")
    print("=" * 50)
    
    # Generate all required keys
    secret_key = generate_secret_key(32)
    jwt_secret = generate_jwt_secret(64)
    encryption_key = generate_encryption_key()
    
    print("\n📋 Copy these values to your Railway environment variables:")
    print("-" * 50)
    
    print(f"\n🔑 SECRET_KEY:")
    print(f"{secret_key}")
    
    print(f"\n🔑 JWT_SECRET_KEY:")
    print(f"{jwt_secret}")
    
    print(f"\n🔑 ENCRYPTION_KEY:")
    print(f"{encryption_key}")
    
    print(f"\n📝 FLASK_ENV:")
    print(f"production")
    
    print(f"\n📝 ENABLE_RATE_LIMITING:")
    print(f"true")
    
    print("\n" + "=" * 50)
    print("📋 ALL 11 ENVIRONMENT VARIABLES FOR RAILWAY:")
    print("-" * 50)
    
    print("\n🔐 ESSENTIAL (Required):")
    print("1. DATABASE_URL (Auto-configured by Railway)")
    print("2. SECRET_KEY (Generated above)")
    print("3. JWT_SECRET_KEY (Generated above)")
    print("4. ENCRYPTION_KEY (Generated above)")
    print("5. FLASK_ENV=production")
    print("6. ENABLE_RATE_LIMITING=true")
    
    print("\n💳 PAYMENT (Stripe):")
    print("7. STRIPE_SECRET_KEY=sk_live_...")
    print("8. STRIPE_PUBLISHABLE_KEY=pk_live_...")
    
    print("\n🤖 AI (Claude):")
    print("9. CLAUDE_API_KEY=sk-ant-...")
    
    print("\n📧 EMAIL:")
    print("10. MAIL_SERVER=smtp.gmail.com")
    print("11. MAIL_PORT=587")
    print("12. MAIL_USERNAME=your-email@domain.com")
    print("13. MAIL_PASSWORD=your-app-password")
    print("14. MAIL_DEFAULT_SENDER=your-email@domain.com")
    
    print("\n⚡ OPTIONAL:")
    print("15. REDIS_URL=redis://... (if using Redis)")
    
    print("\n" + "=" * 50)
    print("✅ All keys generated successfully!")
    print("\n📋 Next steps:")
    print("1. Go to Railway Dashboard")
    print("2. Add these environment variables")
    print("3. Deploy your application")
    print("4. Update your desktop app API URLs")
    
    # Save to file for reference
    with open("railway_env_vars.txt", "w") as f:
        f.write("# Railway Environment Variables - ALL 11 VARIABLES\n")
        f.write("# Generated on: " + str(__import__("datetime").datetime.now()) + "\n\n")
        f.write("# ESSENTIAL (Required)\n")
        f.write("# DATABASE_URL=postgresql://... (Auto-configured by Railway)\n")
        f.write(f"SECRET_KEY={secret_key}\n")
        f.write(f"JWT_SECRET_KEY={jwt_secret}\n")
        f.write(f"ENCRYPTION_KEY={encryption_key}\n")
        f.write(f"FLASK_ENV=production\n")
        f.write(f"ENABLE_RATE_LIMITING=true\n\n")
        
        f.write("# PAYMENT (Stripe)\n")
        f.write("STRIPE_SECRET_KEY=sk_live_...\n")
        f.write("STRIPE_PUBLISHABLE_KEY=pk_live_...\n\n")
        
        f.write("# AI (Claude)\n")
        f.write("CLAUDE_API_KEY=sk-ant-...\n\n")
        
        f.write("# EMAIL\n")
        f.write("MAIL_SERVER=smtp.gmail.com\n")
        f.write("MAIL_PORT=587\n")
        f.write("MAIL_USERNAME=your-email@domain.com\n")
        f.write("MAIL_PASSWORD=your-app-password\n")
        f.write("MAIL_DEFAULT_SENDER=your-email@domain.com\n\n")
        
        f.write("# OPTIONAL\n")
        f.write("REDIS_URL=redis://...\n")
    
    print(f"\n💾 Environment variables saved to: railway_env_vars.txt")

if __name__ == "__main__":
    main() 