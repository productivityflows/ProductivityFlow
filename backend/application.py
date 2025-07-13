import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import string
import logging

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
    raise ValueError("DATABASE_URL environment variable is required")

# Fix postgres:// URL if needed (Render sometimes uses postgres:// instead of postgresql://)
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

application.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

db = SQLAlchemy(application)

# --- Database Models ---
class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)

class Membership(db.Model):
    __tablename__ = 'memberships'
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

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
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

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
            team_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            
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
        
        user_id = generate_id("user")
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
            "userName": user_name
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

if __name__ == '__main__':
    application.run(debug=True)