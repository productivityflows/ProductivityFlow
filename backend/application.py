import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import string

application = Flask(__name__)
CORS(application)

# --- Database Configuration ---
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

# --- Database Models ---
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

@application.route('/api/teams/join', methods=['POST'])
def join_team():
    data = request.get_json()
    user_name = data.get('name', 'New User')
    team_code = data.get('team_code')
    target_team = Team.query.filter_by(code=team_code).first()
    if not target_team:
        return jsonify({"error": "Invalid team code"}), 404
    
    user_id = f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
    new_membership = Membership(team_id=target_team.id, user_id=user_id, user_name=user_name, role="member")
    db.session.add(new_membership)
    db.session.commit()
    
    response_data = {"teamId": target_team.id, "teamName": target_team.name, "userId": user_id, "userName": user_name}
    return jsonify(response_data)

# Command to create database tables
@application.cli.command("create-db")
def create_db_command():
    with application.app_context():
        db.create_all()
    print("Database tables created!")