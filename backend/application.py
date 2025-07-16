import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import string
import logging
import hashlib
import time
import jwt
import bcrypt
from datetime import datetime, timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import redis
import stripe
import anthropic
from cryptography.fernet import Fernet
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import json
import base64

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

application = Flask(__name__)

# --- Enhanced Security & API Key Management ---
# Initialize encryption for secure API key storage
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')
if not ENCRYPTION_KEY:
    # Generate a new key if not provided (for development)
    ENCRYPTION_KEY = Fernet.generate_key()
    logging.warning("No ENCRYPTION_KEY provided, using generated key (dev only)")
else:
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode()

cipher_suite = Fernet(ENCRYPTION_KEY)

# --- Security Configuration ---
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
application.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

# --- Rate Limiting Configuration ---
# Configure Redis for rate limiting (fallback to memory if Redis not available)
try:
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    limiter = Limiter(
        application,
        key_func=get_remote_address,
        storage_uri=redis_url,
        default_limits=["1000 per hour"]
    )
    logging.info("Rate limiting configured with Redis")
except Exception as e:
    logging.warning(f"Redis not available, using in-memory rate limiting: {e}")
    limiter = Limiter(
        application,
        key_func=get_remote_address,
        default_limits=["1000 per hour"]
    )

# --- Stripe Configuration ---
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_live_51RkaYhHHYuKoTuQQMGbXRhWQXBKR5JiFawdfBL7zrOHsay46EoEyYInWesRUUave2x68JY56lXFuYmFmREIHtLeP00YxMFIHTd')

# --- Claude AI Configuration ---
# Encrypt and store Claude API key securely
CLAUDE_API_KEY_ENCRYPTED = os.environ.get('CLAUDE_API_KEY_ENCRYPTED')
if not CLAUDE_API_KEY_ENCRYPTED:
    # Encrypt the provided API key from environment variable
    claude_key = os.environ.get('CLAUDE_API_KEY', 'your-claude-api-key-here')
    if claude_key != 'your-claude-api-key-here':
        CLAUDE_API_KEY_ENCRYPTED = cipher_suite.encrypt(claude_key.encode())
        logging.info("Claude API key encrypted and stored securely")
    else:
        logging.warning("Claude API key not set. Please set CLAUDE_API_KEY environment variable.")

# Decrypt Claude API key for use
def get_claude_api_key():
    try:
        if CLAUDE_API_KEY_ENCRYPTED:
            return cipher_suite.decrypt(CLAUDE_API_KEY_ENCRYPTED).decode()
        return None
    except Exception as e:
        logging.error(f"Failed to decrypt Claude API key: {e}")
        return None

# Initialize Claude client
claude_api_key = get_claude_api_key()
if claude_api_key:
    claude_client = anthropic.Anthropic(api_key=claude_api_key)
else:
    logging.warning("Claude client not initialized due to missing API key")
    claude_client = None

# --- Email Configuration ---
application.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
application.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
application.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
application.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

mail = Mail(application)

# --- Enhanced CORS Configuration ---
CORS(application, 
     origins=["http://localhost:1420", "http://localhost:1421", "tauri://localhost", "*"],  # Allow Tauri origins
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
     supports_credentials=False)

# Handle preflight OPTIONS requests for all routes
@application.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'message': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,X-Requested-With,Accept,Origin")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

# --- Database Configuration ---
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    logging.error("DATABASE_URL environment variable is not set!")
    DATABASE_URL = "sqlite:///fallback.db"  # Fallback for testing

# Handle Render's postgres:// vs postgresql:// format
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enhanced connection pooling for scalability
application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 20,  # Increased for better concurrency
    'pool_size': 10,     # Increased pool size
    'echo': False        # Disable SQL logging in production
}

db = SQLAlchemy(application)

# --- Enhanced Database Models ---
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    employee_code = db.Column(db.String(10), unique=True, nullable=False)  # Renamed from 'code'
    created_at = db.Column(db.DateTime, default=db.func.now())

class ManagerInvite(db.Model):
    __tablename__ = 'manager_invites'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    invite_code = db.Column(db.String(12), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    used_by = db.Column(db.String(80), nullable=True)  # user_id who used it
    created_at = db.Column(db.DateTime, default=db.func.now())
    used_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)  # Manager invites expire

class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'employee' or 'manager'
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Ensure unique team-user combinations
    __table_args__ = (db.UniqueConstraint('team_id', 'user_id', name='unique_team_user'),)

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)  # Added index for performance
    team_id = db.Column(db.String(80), nullable=False, index=True)  # Added index for performance
    date = db.Column(db.Date, nullable=False, index=True)  # Added index for performance
    active_app = db.Column(db.String(255), nullable=True)  # Track active application
    window_title = db.Column(db.Text, nullable=True)  # Track window title
    productive_hours = db.Column(db.Float, default=0.0)
    unproductive_hours = db.Column(db.Float, default=0.0)
    idle_time = db.Column(db.Float, default=0.0)  # Track idle time
    goals_completed = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=db.func.now())
    
    # Composite index for better query performance
    __table_args__ = (db.Index('idx_user_team_date', 'user_id', 'team_id', 'date'),)

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'employee' or 'manager'
    start_time = db.Column(db.DateTime, default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    jwt_token_hash = db.Column(db.String(64), nullable=True)  # Store hashed JWT for validation

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)  # Added index
    assigned_to = db.Column(db.String(80), nullable=False, index=True)  # Added index
    assigned_by = db.Column(db.String(80), nullable=False)  # user_id
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed
    created_at = db.Column(db.DateTime, default=db.func.now())
    completed_at = db.Column(db.DateTime, nullable=True)

# New Enhanced Models for SaaS Features

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(80), primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(255), nullable=True)
    reset_token = db.Column(db.String(255), nullable=True)
    reset_token_expires = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    last_login = db.Column(db.DateTime, nullable=True)
    
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False, unique=True, index=True)
    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_subscription_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='inactive')  # active, inactive, cancelled, past_due
    employee_count = db.Column(db.Integer, default=0)
    monthly_cost = db.Column(db.Float, default=0.0)  # $9.99 per employee
    current_period_start = db.Column(db.DateTime, nullable=True)
    current_period_end = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class ProductivityReport(db.Model):
    __tablename__ = 'productivity_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)
    report_date = db.Column(db.DateTime, nullable=False, index=True)
    hour_start = db.Column(db.DateTime, nullable=False)
    hour_end = db.Column(db.DateTime, nullable=False)
    summary = db.Column(db.Text, nullable=False)
    ai_analysis = db.Column(db.Text, nullable=True)
    irregularity_detected = db.Column(db.Boolean, default=False)
    token_count_input = db.Column(db.Integer, default=0)
    token_count_output = db.Column(db.Integer, default=0)
    cost_estimate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Composite index for efficient queries
    __table_args__ = (db.Index('idx_user_team_date_hour', 'user_id', 'team_id', 'report_date'),)

class TokenUsage(db.Model):
    __tablename__ = 'token_usage'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    input_tokens = db.Column(db.Integer, default=0)
    output_tokens = db.Column(db.Integer, default=0)
    cost_estimate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Unique constraint to prevent duplicate daily records
    __table_args__ = (db.UniqueConstraint('user_id', 'team_id', 'date', name='unique_daily_token_usage'),)

class DetailedActivity(db.Model):
    __tablename__ = 'detailed_activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, index=True)
    team_id = db.Column(db.String(80), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, nullable=False, index=True)
    active_app = db.Column(db.String(255), nullable=True)
    window_title = db.Column(db.Text, nullable=True)
    mouse_clicks = db.Column(db.Integer, default=0)
    keyboard_strokes = db.Column(db.Integer, default=0)
    screenshot_hash = db.Column(db.String(64), nullable=True)  # For irregularity detection
    is_idle = db.Column(db.Boolean, default=False)
    productivity_score = db.Column(db.Float, default=0.0)  # 0-100 scale
    
    # Composite index for efficient queries
    __table_args__ = (db.Index('idx_user_team_timestamp', 'user_id', 'team_id', 'timestamp'),)

# --- Auto-create database tables on startup ---
with application.app_context():
    try:
        # Test database connection first
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        logging.info("Database connection successful!")
        
        # Create tables
        db.create_all()
        logging.info("Database tables checked/created successfully!")
    except Exception as e:
        logging.error(f"Error with database: {e}")
        logging.error(f"Database URL: {DATABASE_URL}")

# --- Utility Functions ---
def generate_id(prefix):
    """Generate a unique ID with timestamp and random components"""
    timestamp = int(time.time())
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{timestamp}_{random_part}"

def generate_team_code():
    """Generate a unique employee team code"""
    max_attempts = 100
    
    for attempt in range(max_attempts):
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        code = ''.join(random.choices(chars, k=6))
        
        existing = Team.query.filter_by(employee_code=code).first()
        if not existing:
            return code
    
    # Fallback with timestamp
    timestamp = str(int(time.time()))[-4:]
    base_code = ''.join(random.choices(chars, k=2))
    return f"{base_code}{timestamp}"

def generate_manager_invite_code():
    """Generate a unique manager invite code (longer and more secure)"""
    max_attempts = 100
    
    for attempt in range(max_attempts):
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'
        code = ''.join(random.choices(chars, k=12))  # Longer code for managers
        
        existing = ManagerInvite.query.filter_by(invite_code=code).first()
        if not existing:
            return code
    
    # Fallback with timestamp
    timestamp = str(int(time.time()))[-6:]
    base_code = ''.join(random.choices(chars, k=6))
    return f"{base_code}{timestamp}"

def create_jwt_token(user_id, team_id, role):
    """Create a JWT token for user authentication"""
    payload = {
        'user_id': user_id,
        'team_id': team_id,
        'role': role,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')

def verify_jwt_token(token):
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_manager_role(f):
    """Decorator to require manager role for API endpoints"""
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        if payload.get('role') != 'manager':
            return jsonify({"error": "Manager role required"}), 403
        
        # Add user info to request for use in endpoint
        request.current_user = payload
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_or_create_user(user_name, team_id):
    """Get existing user or create new one - prevents duplicates"""
    # First try to find user by name in the same team
    existing_membership = Membership.query.filter_by(
        user_name=user_name, 
        team_id=team_id
    ).first()
    
    if existing_membership:
        return existing_membership.user_id, existing_membership.user_name
    
    # Create new user
    user_id = generate_id("user")
    return user_id, user_name

# --- Enhanced Security & Authentication Functions ---

def hash_password(password):
    """Hash password securely using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_verification_token():
    """Generate secure verification token"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def send_verification_email(email, token):
    """Send email verification"""
    try:
        msg = Message(
            'Verify Your ProductivityFlow Account',
            recipients=[email]
        )
        verification_link = f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/verify?token={token}"
        msg.body = f"""
        Welcome to ProductivityFlow!
        
        Please click the link below to verify your email address:
        {verification_link}
        
        If you didn't create this account, please ignore this email.
        """
        mail.send(msg)
        return True
    except Exception as e:
        logging.error(f"Failed to send verification email: {e}")
        return False

# --- Claude AI & Productivity Report Functions ---

def generate_productivity_report(user_id, team_id, hour_start, hour_end):
    """Generate AI productivity report for a specific hour"""
    try:
        # Check if Claude client is available
        if not claude_client:
            return None, "Claude AI client not available. Please configure CLAUDE_API_KEY."
            
        # Get detailed activities for the hour
        activities = DetailedActivity.query.filter(
            DetailedActivity.user_id == user_id,
            DetailedActivity.team_id == team_id,
            DetailedActivity.timestamp >= hour_start,
            DetailedActivity.timestamp < hour_end
        ).order_by(DetailedActivity.timestamp).all()
        
        if not activities:
            return None, "No activity data available for this hour"
        
        # Prepare activity data for AI analysis
        activity_summary = []
        total_clicks = sum(a.mouse_clicks for a in activities)
        total_keystrokes = sum(a.keyboard_strokes for a in activities)
        apps_used = list(set(a.active_app for a in activities if a.active_app))
        idle_time = sum(1 for a in activities if a.is_idle)
        
        # Create optimized prompt (under 2100 input tokens)
        prompt = f"""Analyze this 1-hour productivity data for employee report:

Time: {hour_start.strftime('%Y-%m-%d %H:%M')} - {hour_end.strftime('%H:%M')}
Apps used: {', '.join(apps_used[:5])}  # Limit to top 5 apps
Mouse clicks: {total_clicks}
Keystrokes: {total_keystrokes}
Idle periods: {idle_time} minutes
Active periods: {60 - idle_time} minutes

Create a bullet-point productivity summary (max 200 tokens output):
• Focus level and productivity indicators
• Main applications/tasks worked on
• Any irregularities detected (excessive idle time, potential automation tools)
• Overall productivity score (1-10)

Keep response under 200 tokens, focus on key insights only."""

        # Call Claude API with token limits
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=200,  # Limit output tokens
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        report_content = response.content[0].text
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        
        # Calculate cost (Claude 3 Haiku: $0.25/1M input, $1.25/1M output)
        cost = (input_tokens * 0.25 / 1_000_000) + (output_tokens * 1.25 / 1_000_000)
        
        # Detect irregularities
        irregularity_detected = detect_irregularities(activities, total_clicks, total_keystrokes, idle_time)
        
        return {
            'summary': report_content,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'cost': cost,
            'irregularity_detected': irregularity_detected
        }, None
        
    except Exception as e:
        logging.error(f"Error generating productivity report: {e}")
        return None, str(e)

def detect_irregularities(activities, total_clicks, total_keystrokes, idle_time):
    """Detect potential irregularities in activity data"""
    # Check for signs of automation or cheating
    irregularities = []
    
    # Too many clicks in a short time (potential auto-clicker)
    if total_clicks > 3600:  # More than 1 click per second average
        irregularities.append("Excessive mouse clicks detected")
    
    # Repetitive patterns
    if len(activities) > 0:
        click_pattern = [a.mouse_clicks for a in activities]
        if len(set(click_pattern)) == 1 and click_pattern[0] > 0:
            irregularities.append("Repetitive click pattern detected")
    
    # Too much idle time
    if idle_time > 30:  # More than 30 minutes idle
        irregularities.append("Excessive idle time")
    
    return len(irregularities) > 0

def track_token_usage(user_id, team_id, input_tokens, output_tokens, cost):
    """Track and limit token usage per user"""
    today = datetime.now().date()
    
    # Get or create daily usage record
    usage = TokenUsage.query.filter_by(
        user_id=user_id,
        team_id=team_id,
        date=today
    ).first()
    
    if not usage:
        usage = TokenUsage(
            user_id=user_id,
            team_id=team_id,
            date=today,
            input_tokens=0,
            output_tokens=0,
            cost_estimate=0.0
        )
        db.session.add(usage)
    
    # Update usage
    usage.input_tokens += input_tokens
    usage.output_tokens += output_tokens
    usage.cost_estimate += cost
    
    # Check if exceeding $2 daily limit per employee
    if usage.cost_estimate > 2.0:
        logging.warning(f"User {user_id} exceeded $2 daily token limit: ${usage.cost_estimate:.4f}")
        return False  # Prevent further AI usage today
    
    db.session.commit()
    return True

# --- Billing & Stripe Functions ---

def calculate_monthly_cost(employee_count):
    """Calculate monthly cost based on employee count"""
    return employee_count * 9.99

def create_stripe_customer(email, team_id):
    """Create Stripe customer for billing"""
    try:
        customer = stripe.Customer.create(
            email=email,
            metadata={'team_id': team_id}
        )
        return customer
    except Exception as e:
        logging.error(f"Error creating Stripe customer: {e}")
        return None

def create_stripe_subscription(customer_id, employee_count):
    """Create Stripe subscription"""
    try:
        # Create subscription with per-employee pricing
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'ProductivityFlow - Per Employee',
                    },
                    'unit_amount': 999,  # $9.99 in cents
                    'recurring': {
                        'interval': 'month',
                    },
                },
                'quantity': employee_count,
            }],
            payment_behavior='default_incomplete',
            expand=['latest_invoice.payment_intent'],
        )
        return subscription
    except Exception as e:
        logging.error(f"Error creating Stripe subscription: {e}")
        return None

def update_subscription_quantity(subscription_id, new_employee_count):
    """Update subscription quantity when employee count changes"""
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        stripe.Subscription.modify(
            subscription_id,
            items=[{
                'id': subscription['items']['data'][0]['id'],
                'quantity': new_employee_count,
            }]
        )
        return True
    except Exception as e:
        logging.error(f"Error updating subscription quantity: {e}")
        return False

# --- Scheduler for Background Tasks ---

def cleanup_old_reports():
    """Clean up productivity reports older than 1 week"""
    try:
        cutoff_date = datetime.now() - timedelta(days=7)
        deleted_count = ProductivityReport.query.filter(
            ProductivityReport.created_at < cutoff_date
        ).delete()
        db.session.commit()
        logging.info(f"Cleaned up {deleted_count} old productivity reports")
    except Exception as e:
        logging.error(f"Error cleaning up old reports: {e}")

def generate_hourly_reports():
    """Generate productivity reports for all active users"""
    try:
        # Get all active users from the last hour
        hour_ago = datetime.now() - timedelta(hours=1)
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        active_users = db.session.query(DetailedActivity.user_id, DetailedActivity.team_id).filter(
            DetailedActivity.timestamp >= hour_ago
        ).distinct().all()
        
        for user_id, team_id in active_users:
            # Check token usage limits
            today = datetime.now().date()
            usage = TokenUsage.query.filter_by(
                user_id=user_id,
                team_id=team_id,
                date=today
            ).first()
            
            if usage and usage.cost_estimate >= 2.0:
                continue  # Skip users who've exceeded daily limit
            
            # Generate report
            report_data, error = generate_productivity_report(
                user_id, team_id, hour_ago, current_hour
            )
            
            if report_data and not error:
                # Save report
                report = ProductivityReport(
                    user_id=user_id,
                    team_id=team_id,
                    report_date=current_hour,
                    hour_start=hour_ago,
                    hour_end=current_hour,
                    summary=report_data['summary'],
                    irregularity_detected=report_data['irregularity_detected'],
                    token_count_input=report_data['input_tokens'],
                    token_count_output=report_data['output_tokens'],
                    cost_estimate=report_data['cost']
                )
                db.session.add(report)
                
                # Track token usage
                track_token_usage(
                    user_id, team_id,
                    report_data['input_tokens'],
                    report_data['output_tokens'],
                    report_data['cost']
                )
        
        db.session.commit()
        logging.info("Hourly productivity reports generated successfully")
        
    except Exception as e:
        logging.error(f"Error generating hourly reports: {e}")

# Initialize background scheduler
try:
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=cleanup_old_reports, trigger="cron", hour=2, minute=0)  # Daily at 2 AM
    scheduler.add_job(func=generate_hourly_reports, trigger="cron", minute=0)  # Every hour
    scheduler.start()
    logging.info("Background scheduler started successfully")
except Exception as e:
    logging.error(f"Failed to start background scheduler: {e}")
    scheduler = None

# --- API Endpoints ---
@application.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

# --- Enhanced Authentication Endpoints ---

@application.route('/api/auth/register', methods=['POST'])
@limiter.limit("5 per minute")
def register_user():
    """Register new user with email/password"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not email or not password or not name:
            return jsonify({"error": "Email, password, and name are required"}), 400
        
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters"}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "User with this email already exists"}), 409
        
        # Create new user
        user_id = generate_id("user")
        password_hash = hash_password(password)
        verification_token = generate_verification_token()
        
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            verification_token=verification_token
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email
        send_verification_email(email, verification_token)
        
        return jsonify({
            "message": "User registered successfully. Please check your email for verification.",
            "user_id": user_id
        }), 201
        
    except Exception as e:
        logging.error(f"Error in user registration: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per minute")
def login_user():
    """Login user with email/password"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Invalid email or password"}), 401
        
        if not user.is_verified:
            return jsonify({"error": "Please verify your email before logging in"}), 401
        
        # Update last login
        user.last_login = datetime.now()
        db.session.commit()
        
        # Get user's team memberships
        memberships = Membership.query.filter_by(user_id=user.id).all()
        
        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "teams": [{"team_id": m.team_id, "role": m.role} for m in memberships]
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error in user login: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/auth/verify', methods=['POST'])
def verify_email():
    """Verify user email with token"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            return jsonify({"error": "Invalid verification token"}), 400
        
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        
        return jsonify({"message": "Email verified successfully"}), 200
        
    except Exception as e:
        logging.error(f"Error in email verification: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# --- Enhanced Team Management with Email Integration ---

@application.route('/api/teams/join-with-email', methods=['POST'])
@limiter.limit("10 per minute")
def join_team_with_email():
    """Join team using email account and team code"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        team_code = data.get('team_code', '').strip().upper()
        role = data.get('role', 'employee')  # employee or manager
        
        if not email or not team_code:
            return jsonify({"error": "Email and team code are required"}), 400
        
        # Find user by email
        user = User.query.filter_by(email=email, is_verified=True).first()
        if not user:
            return jsonify({"error": "User not found or email not verified"}), 404
        
        # Find team by code
        team = Team.query.filter_by(employee_code=team_code).first()
        if not team:
            return jsonify({"error": "Invalid team code"}), 404
        
        # Check if user is already a member
        existing_membership = Membership.query.filter_by(
            user_id=user.id, 
            team_id=team.id
        ).first()
        
        if existing_membership:
            return jsonify({"error": "User is already a member of this team"}), 409
        
        # Create membership
        membership = Membership(
            team_id=team.id,
            user_id=user.id,
            user_name=user.name,
            role=role
        )
        
        db.session.add(membership)
        
        # Update subscription if this is an employee
        if role == 'employee':
            subscription = Subscription.query.filter_by(team_id=team.id).first()
            if subscription:
                subscription.employee_count += 1
                subscription.monthly_cost = calculate_monthly_cost(subscription.employee_count)
                
                # Update Stripe subscription
                if subscription.stripe_subscription_id:
                    update_subscription_quantity(subscription.stripe_subscription_id, subscription.employee_count)
        
        db.session.commit()
        
        # Create JWT token
        token = create_jwt_token(user.id, team.id, role)
        
        return jsonify({
            "message": "Successfully joined team",
            "token": token,
            "team": {"id": team.id, "name": team.name},
            "user": {"id": user.id, "name": user.name, "role": role}
        }), 200
        
    except Exception as e:
        logging.error(f"Error joining team with email: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Add the rest of the original API endpoints
@application.route('/api/teams', methods=['POST'])
def create_team():
    """Create a new team"""
    try:
        data = request.get_json()
        team_name = data.get('name', '').strip()
        user_name = data.get('user_name', '').strip()
        role = data.get('role', 'manager')
        
        if not team_name or not user_name:
            return jsonify({"error": "Team name and user name are required"}), 400
        
        # Generate unique IDs
        team_id = generate_id("team")
        employee_code = generate_team_code()
        user_id, validated_user_name = get_or_create_user(user_name, team_id)
        
        # Create team
        team = Team(
            id=team_id,
            name=team_name,
            employee_code=employee_code
        )
        
        # Create membership
        membership = Membership(
            team_id=team_id,
            user_id=user_id,
            user_name=validated_user_name,
            role=role
        )
        
        db.session.add(team)
        db.session.add(membership)
        db.session.commit()
        
        # Create JWT token
        token = create_jwt_token(user_id, team_id, role)
        
        logging.info(f"Team created: {team_id} by user: {user_id}")
        
        return jsonify({
            "message": "Team created successfully",
            "token": token,
            "team": {
                "id": team_id,
                "name": team_name,
                "employee_code": employee_code
            },
            "user": {
                "id": user_id,
                "name": validated_user_name,
                "role": role
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error creating team: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

# --- Team Join & Activity Tracking Endpoints ---

@application.route('/api/teams/join', methods=['POST'])
@limiter.limit("10 per minute")
def join_team():
    """Join team using team code (for simple employee tracker without email)"""
    try:
        data = request.get_json()
        team_code = data.get('team_code', '').strip().upper()
        employee_name = data.get('employee_name', '').strip()
        
        if not team_code or not employee_name:
            return jsonify({"error": "Team code and employee name are required"}), 400
        
        # Find team by code
        team = Team.query.filter_by(employee_code=team_code).first()
        if not team:
            return jsonify({"error": "Invalid team code"}), 404
        
        # Generate a temporary user ID for the session
        user_id = f"emp_{hashlib.md5((team_code + employee_name).encode()).hexdigest()[:8]}"
        
        # Check if user is already a member
        existing_membership = Membership.query.filter_by(
            user_id=user_id, 
            team_id=team.id
        ).first()
        
        if not existing_membership:
            # Create membership for temporary user
            membership = Membership(
                team_id=team.id,
                user_id=user_id,
                user_name=employee_name,
                role='employee'
            )
            db.session.add(membership)
            db.session.commit()
        
        # Generate JWT token
        token_payload = {
            'user_id': user_id,
            'team_id': team.id,
            'role': 'employee',
            'exp': datetime.utcnow() + timedelta(days=30)  # 30 day expiry
        }
        token = jwt.encode(token_payload, application.config['JWT_SECRET_KEY'], algorithm='HS256')
        
        return jsonify({
            "success": True,
            "token": token,
            "user": {
                "id": user_id,
                "name": employee_name,
                "role": "employee"
            },
            "team": {
                "id": team.id,
                "name": team.name,
                "code": team.employee_code
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error joining team: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@application.route('/api/teams/<team_id>/activity', methods=['POST'])
@limiter.limit("120 per minute")  # Higher limit for activity tracking
def submit_activity(team_id):
    """Submit activity data for a team member"""
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            # Decode JWT token
            payload = jwt.decode(token, application.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = payload.get('user_id')
            token_team_id = payload.get('team_id')
            
            # Verify team ID matches
            if token_team_id != team_id:
                return jsonify({"error": "Token team ID does not match request"}), 403
                
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        data = request.get_json()
        
        # Extract activity data
        active_app = data.get('activeApp', '')
        window_title = data.get('windowTitle', '')
        idle_time = data.get('idleTime', 0.0)
        productive_hours = data.get('productiveHours', 0.0)
        unproductive_hours = data.get('unproductiveHours', 0.0)
        goals_completed = data.get('goalsCompleted', 0)
        
        # Get or create today's activity record
        today = datetime.utcnow().date()
        activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=today
        ).first()
        
        if not activity:
            activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=today
            )
            db.session.add(activity)
        
        # Update activity data
        activity.active_app = active_app
        activity.window_title = window_title
        activity.idle_time = idle_time
        activity.productive_hours = productive_hours
        activity.unproductive_hours = unproductive_hours
        activity.goals_completed = goals_completed
        activity.last_active = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Activity data recorded successfully"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error submitting activity: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# --- Version & Update Endpoints ---

@application.route('/api/version', methods=['GET'])
def get_version():
    """Get current application version for auto-updater"""
    return jsonify({
        "version": "1.0.0",
        "build_date": "2024-01-15",
        "download_urls": {
            "windows_tracker": "/downloads/tracker-windows.exe",
            "mac_tracker": "/downloads/tracker-mac.dmg",
            "windows_dashboard": "/downloads/dashboard-windows.exe",
            "mac_dashboard": "/downloads/dashboard-mac.dmg"
        }
    }), 200

@application.route('/api/config/stripe', methods=['GET'])
def get_stripe_config():
    """Get Stripe publishable key for frontend"""
    return jsonify({
        "publishable_key": STRIPE_PUBLISHABLE_KEY
    }), 200

# Graceful shutdown
import atexit

def shutdown_scheduler():
    """Shutdown the background scheduler gracefully"""
    if scheduler:
        try:
            scheduler.shutdown()
            logging.info("Background scheduler shut down successfully")
        except Exception as e:
            logging.error(f"Error shutting down scheduler: {e}")

# Register shutdown handler
atexit.register(shutdown_scheduler)

# --- Database Initialization ---
def init_db():
    """Initialize database tables"""
    try:
        with application.app_context():
            db.create_all()
            logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error creating database tables: {e}")

# Initialize database when the app starts
@application.before_first_request
def create_tables():
    """Create database tables before first request"""
    init_db()

# CLI command for manual database creation
@application.cli.command('create-db')
def create_db_command():
    """Create database tables via CLI"""
    init_db()
    print("Database tables created!")

if __name__ == '__main__':
    # Initialize database tables
    init_db()
    application.run(debug=True)