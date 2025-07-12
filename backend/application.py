import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Import the library
import random
import string

application = Flask(__name__)

# --- CORS CONFIGURATION ---
# This uses the Flask-Cors library to handle all CORS requests automatically
CORS(application)
# --- END OF CONFIGURATION ---

# Database Configuration
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

# ... (Your database models like Team, Membership, etc. go here) ...
class Team(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)
    owner_id = db.Column(db.String(80), nullable=False)

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)


# --- API Routes ---
@application.route('/')
def health_check():
    return jsonify({"status": "healthy"}), 200

@application.route('/api/teams', methods=['POST', 'GET'])
def handle_teams():
    if request.method == 'GET':
        teams = Team.query.all()
        return jsonify({"teams": [{"id": t.id, "name": t.name, "code": t.code, "memberCount": Membership.query.filter_by(team_id=t.id).count()} for t in teams]})
    if request.method == 'POST':
        data = request.get_json()
        team_id = f"team_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        new_team = Team(id=team_id, name=data['name'], code=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)), owner_id="manager-01")
        db.session.add(new_team)
        manager_membership = Membership(team_id=team_id, user_id="manager-01", user_name="Alex Manager", role="owner")
        db.session.add(manager_membership)
        db.session.commit()
        return jsonify({"id": new_team.id, "name": new_team.name, "code": new_team.code, "memberCount": 1})
        
# Add your other API routes here...

# This command allows us to create the database tables
@application.cli.command("create-db")
def create_db_command():
    """Creates the database tables."""
    with application.app_context():
        db.create_all()
    print("Database tables created!")