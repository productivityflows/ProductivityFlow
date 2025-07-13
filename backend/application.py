import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import string
import logging
import hashlib
import time
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.INFO)

application = Flask(__name__)

# --- Enhanced CORS Configuration ---
# More permissive CORS for all Vercel deployments
CORS(application, 
     origins="*",  # Allow all origins temporarily for debugging
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

# Add connection pooling and error recovery
application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 10
}

db = SQLAlchemy(application)

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    joined_at = db.Column(db.DateTime, default=db.func.now())
    
    # Add unique constraint to prevent duplicate memberships
    __table_args__ = (db.UniqueConstraint('team_id', 'user_id', name='unique_team_user'),)

class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    productive_hours = db.Column(db.Float, default=0.0)
    unproductive_hours = db.Column(db.Float, default=0.0)
    goals_completed = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=db.func.now())

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False)
    team_id = db.Column(db.String(80), nullable=False)
    start_time = db.Column(db.DateTime, default=db.func.now())
    end_time = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    assigned_to = db.Column(db.String(80), nullable=False)  # user_id
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

def generate_id(prefix):
    """Generate a unique ID with timestamp and random components"""
    timestamp = int(time.time())
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}_{timestamp}_{random_part}"

def generate_team_code():
    """Generate a unique team code with better collision avoidance"""
    max_attempts = 100
    
    for attempt in range(max_attempts):
        # Use a mix of uppercase letters and numbers for better readability
        # Avoid confusing characters like 0, O, I, 1
        chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
        
        # Generate 6-character code
        code = ''.join(random.choices(chars, k=6))
        
        # Check if code already exists
        existing = Team.query.filter_by(code=code).first()
        if not existing:
            return code
    
    # If we somehow can't generate a unique code, add timestamp
    timestamp = str(int(time.time()))[-4:]  # Last 4 digits of timestamp
    base_code = ''.join(random.choices(chars, k=2))
    return f"{base_code}{timestamp}"

def get_or_create_user(user_name, team_id):
    """Get existing user or create new one - prevents duplicates"""
    # First try to find user by name in the same team
    existing_membership = Membership.query.filter_by(
        user_name=user_name, 
        team_id=team_id
    ).first()
    
    if existing_membership:
        return existing_membership.user_id, existing_membership.user_name
    
    # Check if user exists in other teams (to reuse user_id)
    existing_user = Membership.query.filter_by(user_name=user_name).first()
    if existing_user:
        return existing_user.user_id, existing_user.user_name
    
    # Create new user
    user_id = generate_id("user")
    return user_id, user_name

# --- Health Check Route ---
@application.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        with db.engine.connect() as connection:
            connection.execute(db.text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

# --- API Routes ---
@application.route('/api/teams', methods=['POST', 'GET', 'OPTIONS'])
def handle_teams():
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    try:
        if request.method == 'GET':
            logging.info("Fetching teams from database...")
            teams = Team.query.all()
            logging.info(f"Found {len(teams)} teams")
            return jsonify({"teams": [{"id": t.id, "name": t.name, "code": t.code} for t in teams]})
            
        if request.method == 'POST':
            data = request.get_json()
            if not data or not data.get('name'):
                return jsonify({"error": "Team name is required"}), 400
                
            team_id = generate_id("team")
            team_code = generate_team_code()
            
            new_team = Team(id=team_id, name=data['name'], code=team_code)
            db.session.add(new_team)
            db.session.commit()
            logging.info(f"Created new team: {team_id}")
            
            return jsonify({"id": new_team.id, "name": new_team.name, "code": new_team.code, "memberCount": 1})
            
    except Exception as e:
        logging.error(f"Error in /api/teams: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/join', methods=['POST', 'OPTIONS'])
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
            
        logging.info(f"Looking for team with code: {team_code}")
        target_team = Team.query.filter_by(code=team_code).first()
        
        if not target_team:
            return jsonify({"error": "Invalid team code"}), 404
        
        user_id, user_name = get_or_create_user(user_name, target_team.id)
        
        # Check if user is already a member of this team
        existing_membership = Membership.query.filter_by(
            team_id=target_team.id,
            user_id=user_id
        ).first()
        
        if existing_membership:
            logging.info(f"User {user_name} already member of team {target_team.name}")
            return jsonify({
                "teamId": target_team.id, 
                "teamName": target_team.name, 
                "userId": user_id, 
                "userName": user_name,
                "message": "Already a member"
            })
        
        new_membership = Membership(
            team_id=target_team.id, 
            user_id=user_id, 
            user_name=user_name, 
            role="member"
        )
        db.session.add(new_membership)
        db.session.commit()
        
        logging.info(f"User {user_name} joined team {target_team.name}")
        
        return jsonify({
            "teamId": target_team.id, 
            "teamName": target_team.name, 
            "userId": user_id, 
            "userName": user_name,
            "message": "Successfully joined team"
        })
        
    except Exception as e:
        logging.error(f"Error in /api/teams/join: {e}")
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/members', methods=['GET', 'OPTIONS'])
def get_team_members(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    try:
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
                "goalsCompleted": activity.goals_completed if activity else 0,
                "isActive": active_session is not None,
                "lastActive": activity.last_active.isoformat() if activity else None
            })
        
        return jsonify({"members": member_data})
        
    except Exception as e:
        logging.error(f"Error in /api/teams/{team_id}/members: {e}")
        return jsonify({"error": "Internal Server Error", "details": str(e)}), 500

@application.route('/api/teams/<team_id>/stats', methods=['GET', 'OPTIONS'])
def get_team_stats(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    try:
        # Get today's date
        today = db.func.date(db.func.now())
        
        # Get total team hours for today
        total_hours = db.session.query(
            db.func.sum(Activity.productive_hours + Activity.unproductive_hours)
        ).filter_by(team_id=team_id, date=today).scalar() or 0
        
        # Get average productivity (productive hours / total hours)
        total_productive = db.session.query(
            db.func.sum(Activity.productive_hours)
        ).filter_by(team_id=team_id, date=today).scalar() or 0
        
        avg_productivity = (total_productive / total_hours * 100) if total_hours > 0 else 0
        
        # Get total goals completed today
        total_goals = db.session.query(
            db.func.sum(Activity.goals_completed)
        ).filter_by(team_id=team_id, date=today).scalar() or 0
        
        # Get active members count
        active_members = UserSession.query.filter_by(
            team_id=team_id,
            is_active=True
        ).count()
        
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
def track_activity(team_id):
    # Handle preflight OPTIONS request
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    try:
        data = request.get_json()
        user_id = data.get('userId')
        productive_hours = data.get('productiveHours', 0)
        unproductive_hours = data.get('unproductiveHours', 0)
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
            activity.goals_completed = goals_completed
            activity.last_active = db.func.now()
        else:
            activity = Activity(
                user_id=user_id,
                team_id=team_id,
                date=today,
                productive_hours=productive_hours,
                unproductive_hours=unproductive_hours,
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
            session = UserSession(
                user_id=user_id,
                team_id=team_id,
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
            # Get recent activity data (last 7 days)
            recent_activities = Activity.query.filter(
                Activity.user_id == member.user_id,
                Activity.team_id == team_id,
                Activity.date >= datetime.now().date() - timedelta(days=7)
            ).all()
            
            total_productive = sum(a.productive_hours for a in recent_activities)
            total_unproductive = sum(a.unproductive_hours for a in recent_activities)
            total_hours = total_productive + total_unproductive
            
            # Calculate efficiency percentage
            efficiency = (total_productive / total_hours * 100) if total_hours > 0 else 0
            
            # Get task completion rate
            total_tasks = Task.query.filter_by(team_id=team_id, assigned_to=member.user_id).count()
            completed_tasks = Task.query.filter_by(
                team_id=team_id, 
                assigned_to=member.user_id, 
                status='completed'
            ).count()
            
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