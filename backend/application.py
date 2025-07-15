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

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)

application = Flask(__name__)

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

# --- Enhanced CORS Configuration ---
CORS(application, 
     origins="*",  # In production, specify exact origins
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
     supports_credentials=False)

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

# --- API Endpoints ---
@application.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Test database connection
        db.session.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        logging.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@application.route('/api/teams', methods=['POST', 'GET', 'OPTIONS'])
@limiter.limit("100 per hour")  # Rate limit team creation
def manage_teams():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
    
    try:
        if request.method == 'GET':
            # Get all teams (limited info for public endpoint)
            teams = Team.query.all()
            team_list = []
            
            for t in teams:
                member_count = Membership.query.filter_by(team_id=t.id).count()
                team_list.append({
                    "id": t.id, 
                    "name": t.name, 
                    "employee_code": t.employee_code,
                    "memberCount": member_count
                })
            
            return jsonify({"teams": team_list})
            
        if request.method == 'POST':
            data = request.get_json()
            if not data or not data.get('name'):
                return jsonify({"error": "Team name is required"}), 400
                
            team_id = generate_id("team")
            employee_code = generate_team_code()
            manager_invite_code = generate_manager_invite_code()
            
            # Create team
            new_team = Team(id=team_id, name=data['name'], employee_code=employee_code)
            db.session.add(new_team)
            
            # Create manager invite (expires in 30 days)
            manager_invite = ManagerInvite(
                team_id=team_id,
                invite_code=manager_invite_code,
                expires_at=datetime.utcnow() + timedelta(days=30)
            )
            db.session.add(manager_invite)
            
            db.session.commit()
            logging.info(f"Created new team: {team_id}")
            
            return jsonify({
                "id": new_team.id, 
                "name": new_team.name, 
                "employee_code": new_team.employee_code,
                "manager_invite_code": manager_invite_code,  # Return this only once
                "memberCount": 0
            })
            
    except Exception as e:
        logging.error(f"Error in /api/teams: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/join', methods=['POST', 'OPTIONS'])
@limiter.limit("10 per minute")  # Rate limit employee joins
def join_team():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_name = data.get('name', 'New User')
        team_code = data.get('team_code')
        
        if not team_code:
            return jsonify({"error": "Team code is required"}), 400
            
        logging.info(f"Looking for team with employee code: {team_code}")
        target_team = Team.query.filter_by(employee_code=team_code).first()
        
        if not target_team:
            return jsonify({"error": "Invalid team code"}), 404
        
        user_id, user_name = get_or_create_user(user_name, target_team.id)
        
        # Check if user is already a member of this team
        existing_membership = Membership.query.filter_by(
            team_id=target_team.id,
            user_id=user_id
        ).first()
        
        if existing_membership:
            # Create JWT token for existing member
            token = create_jwt_token(user_id, target_team.id, existing_membership.role)
            
            logging.info(f"User {user_name} already member of team {target_team.name}")
            return jsonify({
                "teamId": target_team.id, 
                "teamName": target_team.name, 
                "userId": user_id, 
                "userName": user_name,
                "role": existing_membership.role,
                "token": token,
                "message": "Already a member"
            })
        
        # Create new employee membership
        new_membership = Membership(
            team_id=target_team.id, 
            user_id=user_id, 
            user_name=user_name, 
            role="employee"
        )
        db.session.add(new_membership)
        
        # Create user session
        session = UserSession(
            user_id=user_id,
            team_id=target_team.id,
            role="employee",
            is_active=True
        )
        db.session.add(session)
        
        db.session.commit()
        
        # Create JWT token
        token = create_jwt_token(user_id, target_team.id, "employee")
        
        logging.info(f"User {user_name} joined team {target_team.name} as employee")
        
        return jsonify({
            "teamId": target_team.id, 
            "teamName": target_team.name, 
            "userId": user_id, 
            "userName": user_name,
            "role": "employee",
            "token": token,
            "message": "Successfully joined team"
        })
        
    except Exception as e:
        logging.error(f"Error in /api/teams/join: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/claim-manager-role', methods=['POST', 'OPTIONS'])
@limiter.limit("5 per minute")  # Stricter rate limit for manager role
def claim_manager_role():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_name = data.get('name', 'New Manager')
        manager_invite_code = data.get('manager_invite_code')
        
        if not manager_invite_code:
            return jsonify({"error": "Manager invite code is required"}), 400
            
        logging.info(f"Looking for manager invite with code: {manager_invite_code}")
        
        # Find the manager invite
        invite = ManagerInvite.query.filter_by(invite_code=manager_invite_code).first()
        
        if not invite:
            return jsonify({"error": "Invalid manager invite code"}), 404
        
        # Check if invite is still valid
        if invite.is_used:
            return jsonify({"error": "Manager invite code has already been used"}), 400
        
        if invite.expires_at < datetime.utcnow():
            return jsonify({"error": "Manager invite code has expired"}), 400
        
        # Get the team
        target_team = Team.query.filter_by(id=invite.team_id).first()
        if not target_team:
            return jsonify({"error": "Team not found"}), 404
        
        user_id, user_name = get_or_create_user(user_name, target_team.id)
        
        # Check if user is already a manager of this team
        existing_membership = Membership.query.filter_by(
            team_id=target_team.id,
            user_id=user_id
        ).first()
        
        if existing_membership:
            # Update role to manager
            existing_membership.role = "manager"
        else:
            # Create new manager membership
            new_membership = Membership(
                team_id=target_team.id, 
                user_id=user_id, 
                user_name=user_name, 
                role="manager"
            )
            db.session.add(new_membership)
        
        # Mark invite as used
        invite.is_used = True
        invite.used_by = user_id
        invite.used_at = datetime.utcnow()
        
        # Create manager session
        session = UserSession(
            user_id=user_id,
            team_id=target_team.id,
            role="manager",
            is_active=True
        )
        db.session.add(session)
        
        db.session.commit()
        
        # Create JWT token
        token = create_jwt_token(user_id, target_team.id, "manager")
        
        logging.info(f"User {user_name} claimed manager role for team {target_team.name}")
        
        return jsonify({
            "teamId": target_team.id, 
            "teamName": target_team.name, 
            "userId": user_id, 
            "userName": user_name,
            "role": "manager",
            "token": token,
            "message": "Successfully claimed manager role"
        })
        
    except Exception as e:
        logging.error(f"Error in /api/teams/claim-manager-role: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/members', methods=['GET', 'OPTIONS'])
@require_manager_role  # Require manager role to view team members
def get_team_members(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
        
    try:
        # Verify team exists and user has access
        if request.current_user['team_id'] != team_id:
            return jsonify({"error": "Access denied to this team"}), 403
        
        # Get team members
        members = Membership.query.filter_by(team_id=team_id).all()
        
        # Get activity data for each member
        member_data = []
        for member in members:
            # Get today's activity
            today = db.func.date(db.func.now())
            activity = Activity.query.filter_by(
                user_id=member.user_id, 
                team_id=team_id,
                date=today
            ).first()
            
            # Check if user is currently active
            active_session = UserSession.query.filter_by(
                user_id=member.user_id,
                team_id=team_id,
                is_active=True
            ).first()
            
            member_data.append({
                "userId": member.user_id,
                "name": member.user_name,
                "role": member.role,
                "productiveHours": activity.productive_hours if activity else 0,
                "unproductiveHours": activity.unproductive_hours if activity else 0,
                "idleTime": activity.idle_time if activity else 0,
                "goalsCompleted": activity.goals_completed if activity else 0,
                "isActive": active_session is not None,
                "lastActive": activity.last_active.isoformat() if activity and activity.last_active else None,
                "activeApp": activity.active_app if activity else None,
                "windowTitle": activity.window_title if activity else None
            })
        
        return jsonify({"members": member_data})
        
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/members: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/stats', methods=['GET', 'OPTIONS'])
@require_manager_role  # Require manager role to view team stats
def get_team_stats(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
        
    try:
        # Verify team exists and user has access
        if request.current_user['team_id'] != team_id:
            return jsonify({"error": "Access denied to this team"}), 403
        
        # Get today's date
        today = db.func.date(db.func.now())
        
        # Get total team hours for today (with fallback if Activity table doesn't exist)
        try:
            total_hours = db.session.query(
                db.func.sum(Activity.productive_hours + Activity.unproductive_hours)
            ).filter_by(team_id=team_id, date=today).scalar() or 0
            
            # Get average productivity (productive hours / total hours)
            total_productive = db.session.query(
                db.func.sum(Activity.productive_hours)
            ).filter_by(team_id=team_id, date=today).scalar() or 0
        except Exception as e:
            logging.warning(f"Activity table may not exist: {e}")
            total_hours = 0
            total_productive = 0
        
        avg_productivity = (total_productive / total_hours * 100) if total_hours > 0 else 0
        
        # Get total goals completed today (with fallback if Activity table doesn't exist)
        try:
            total_goals = db.session.query(
                db.func.sum(Activity.goals_completed)
            ).filter_by(team_id=team_id, date=today).scalar() or 0
        except Exception as e:
            logging.warning(f"Activity table may not exist: {e}")
            total_goals = 0
        
        # Get active members count (with fallback if UserSession table doesn't exist)
        try:
            active_members = UserSession.query.filter_by(
                team_id=team_id,
                is_active=True
            ).count()
        except Exception as e:
            logging.warning(f"UserSession table may not exist: {e}")
            active_members = 0
        
        # Get total members count
        total_members = Membership.query.filter_by(team_id=team_id).count()
        
        return jsonify({
            "totalHours": round(total_hours, 1),
            "avgProductivity": round(avg_productivity, 1),
            "goalsCompleted": total_goals,
            "activeMembers": active_members,
            "totalMembers": total_members,
            "hoursChange": "+12%",  # Placeholder for now
            "productivityChange": "+5%"  # Placeholder for now
        })
        
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/stats: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/activity', methods=['POST', 'OPTIONS'])
@limiter.limit("60 per minute")  # Rate limit activity tracking
def track_activity(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response
        
    try:
        # Verify JWT token for activity tracking
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = verify_jwt_token(token)
            if payload and payload.get('team_id') != team_id:
                return jsonify({"error": "Access denied to this team"}), 403
        
        data = request.get_json()
        user_id = data.get('userId')
        productive_hours = data.get('productiveHours', 0)
        unproductive_hours = data.get('unproductiveHours', 0)
        idle_time = data.get('idleTime', 0)  # New field
        active_app = data.get('activeApp')  # New field
        window_title = data.get('windowTitle')  # New field
        goals_completed = data.get('goalsCompleted', 0)
        
        if not user_id:
            return jsonify({"error": "User ID is required"}), 400
        
        # Get today's date
        today = db.func.date(db.func.now())
        
        # Update or create activity record
        activity = Activity.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            date=today
        ).first()
        
        if activity:
            activity.productive_hours = productive_hours
            activity.unproductive_hours = unproductive_hours
            activity.idle_time = idle_time
            activity.active_app = active_app
            activity.window_title = window_title
            activity.goals_completed = goals_completed
            activity.last_active = db.func.now()
        else:
            activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=today,
                productive_hours=productive_hours,
                unproductive_hours=unproductive_hours,
                idle_time=idle_time,
                active_app=active_app,
                window_title=window_title,
                goals_completed=goals_completed
            )
            db.session.add(activity)
        
        # Update user session
        session = UserSession.query.filter_by(
            user_id=user_id,
            team_id=team_id,
            is_active=True
        ).first()
        
        if not session:
            # Determine role from membership
            membership = Membership.query.filter_by(
                user_id=user_id,
                team_id=team_id
            ).first()
            
            session = UserSession(
                user_id=user_id,
                team_id=team_id,
                role=membership.role if membership else "employee",
                is_active=True
            )
            db.session.add(session)
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Activity tracked successfully"})
        
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/activity: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/sample-data', methods=['POST', 'OPTIONS'])
def add_sample_data(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        import datetime
        import random
        
        # Get all members of the team
        members = Membership.query.filter_by(team_id=team_id).all()
        
        if not members:
            return jsonify({"error": "No members found in this team"}), 404
        
        today = datetime.date.today()
        
        # Add sample activity data for each member
        for member in members:
            # Check if activity already exists for today
            existing_activity = Activity.query.filter_by(
                user_id=member.user_id,
                team_id=team_id,
                date=today
            ).first()
            
            if not existing_activity:
                # Create random activity data
                productive_hours = round(random.uniform(4, 8), 1)
                unproductive_hours = round(random.uniform(0.5, 2), 1)
                goals_completed = random.randint(2, 8)
                
                activity = Activity(
                    user_id=member.user_id,
                    team_id=team_id,
                    date=today,
                    productive_hours=productive_hours,
                    unproductive_hours=unproductive_hours,
                    goals_completed=goals_completed
                )
                db.session.add(activity)
            
            # Add user session (make some active)
            existing_session = UserSession.query.filter_by(
                user_id=member.user_id,
                team_id=team_id,
                is_active=True
            ).first()
            
            if not existing_session and random.choice([True, False]):
                session = UserSession(
                    user_id=member.user_id,
                    team_id=team_id,
                    is_active=True
                )
                db.session.add(session)
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Sample data added successfully"})
        
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/sample-data: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/tasks', methods=['GET', 'POST', 'OPTIONS'])
def handle_tasks(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        if request.method == 'GET':
            # Get all tasks for the team
            tasks = Task.query.filter_by(team_id=team_id).all()
            
            task_list = []
            for task in tasks:
                # Get assignee name
                assignee = Membership.query.filter_by(
                    team_id=team_id,
                    user_id=task.assigned_to
                ).first()
                
                # Get assigner name
                assigner = Membership.query.filter_by(
                    team_id=team_id,
                    user_id=task.assigned_by
                ).first()
                
                task_list.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "assignedTo": assignee.user_name if assignee else "Unknown",
                    "assignedBy": assigner.user_name if assigner else "Unknown",
                    "dueDate": task.due_date.isoformat(),
                    "status": task.status,
                    "createdAt": task.created_at.isoformat(),
                    "completedAt": task.completed_at.isoformat() if task.completed_at else None
                })
            
            return jsonify({"tasks": task_list})
        
        elif request.method == 'POST':
            # Create new task
            data = request.get_json()
            
            # Validate required fields
            if not all(k in data for k in ('title', 'assignedTo', 'assignedBy', 'dueDate')):
                return jsonify({"error": "Missing required fields"}), 400
            
            # Parse due date
            due_date = datetime.fromisoformat(data['dueDate'].replace('Z', '+00:00'))
            
            task = Task(
                team_id=team_id,
                assigned_to=data['assignedTo'],
                assigned_by=data['assignedBy'],
                title=data['title'],
                description=data.get('description', ''),
                due_date=due_date
            )
            
            db.session.add(task)
            db.session.commit()
            
            return jsonify({
                "id": task.id,
                "message": "Task created successfully"
            })
    
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/tasks: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/tasks/<int:task_id>', methods=['PUT', 'OPTIONS'])
def update_task(team_id, task_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'PUT, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        task = Task.query.filter_by(id=task_id, team_id=team_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        data = request.get_json()
        
        # Update task fields
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.completed_at = datetime.now()
        
        if 'title' in data:
            task.title = data['title']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'dueDate' in data:
            task.due_date = datetime.fromisoformat(data['dueDate'].replace('Z', '+00:00'))
        
        db.session.commit()
        
        return jsonify({"message": "Task updated successfully"})
    
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/tasks/{task_id}: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/users/<user_id>/tasks', methods=['GET', 'OPTIONS'])
def get_user_tasks(team_id, user_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        # Get tasks assigned to this user
        tasks = Task.query.filter_by(team_id=team_id, assigned_to=user_id).all()
        
        task_list = []
        for task in tasks:
            # Get assigner name
            assigner = Membership.query.filter_by(
                team_id=team_id,
                user_id=task.assigned_by
            ).first()
            
            task_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "assignedBy": assigner.user_name if assigner else "Unknown",
                "dueDate": task.due_date.isoformat(),
                "status": task.status,
                "createdAt": task.created_at.isoformat(),
                "completedAt": task.completed_at.isoformat() if task.completed_at else None
            })
        
        return jsonify({"tasks": task_list})
    
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/users/{user_id}/tasks: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/performance', methods=['GET', 'OPTIONS'])
def get_team_performance(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    
    try:
        # Get all team members with their performance data
        members = Membership.query.filter_by(team_id=team_id).all()
        
        performance_data = []
        for member in members:
            # Get recent activity data (last 7 days) with fallback
            try:
                recent_activities = Activity.query.filter(
                    Activity.user_id == member.user_id,
                    Activity.team_id == team_id,
                    Activity.date >= datetime.now().date() - timedelta(days=7)
                ).all()
                
                total_productive = sum(a.productive_hours for a in recent_activities)
                total_unproductive = sum(a.unproductive_hours for a in recent_activities)
            except Exception as e:
                logging.warning(f"Activity table may not exist: {e}")
                total_productive = 0
                total_unproductive = 0
            
            total_hours = total_productive + total_unproductive
            
            # Calculate efficiency percentage
            efficiency = (total_productive / total_hours * 100) if total_hours > 0 else 0
            
            # Get task completion rate with fallback
            try:
                total_tasks = Task.query.filter_by(team_id=team_id, assigned_to=member.user_id).count()
                completed_tasks = Task.query.filter_by(
                    team_id=team_id, 
                    assigned_to=member.user_id, 
                    status='completed'
                ).count()
            except Exception as e:
                logging.warning(f"Task table may not exist: {e}")
                total_tasks = 0
                completed_tasks = 0
            
            task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Overall score (weighted average)
            overall_score = (efficiency * 0.7) + (task_completion_rate * 0.3)
            
            performance_data.append({
                "userId": member.user_id,
                "userName": member.user_name,
                "efficiency": round(efficiency, 1),
                "taskCompletionRate": round(task_completion_rate, 1),
                "overallScore": round(overall_score, 1),
                "totalHours": round(total_hours, 1),
                "productiveHours": round(total_productive, 1),
                "unproductiveHours": round(total_unproductive, 1),
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks
            })
        
        # Sort by overall score (descending)
        performance_data.sort(key=lambda x: x['overallScore'], reverse=True)
        
        # Categorize performers
        top_performers = [p for p in performance_data if p['overallScore'] >= 90]
        needs_improvement = [p for p in performance_data if p['overallScore'] < 60]
        
        return jsonify({
            "allPerformers": performance_data,
            "topPerformers": top_performers,
            "needsImprovement": needs_improvement
        })
    
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/performance: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

if __name__ == '__main__':
    application.run(debug=True)