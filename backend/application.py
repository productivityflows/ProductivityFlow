import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import random
import string

# The Flask object must be named 'application' for Elastic Beanstalk
application = Flask(__name__)

# --- Database Configuration ---
# Reads the connection URL from the environment variable you set in AWS
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
    team_id = db.Column(db.String(80), db.ForeignKey('team.id'), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

# --- CORS Handling ---
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- Helper functions ---
def generate_id(prefix, length=8):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=length))}"

# --- API Routes (now using the database) ---
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
        team_id = generate_id("team")
        new_team = Team(id=team_id, name=data['name'], code=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)), owner_id="manager-01")
        db.session.add(new_team)
        manager_membership = Membership(team_id=team_id, user_id="manager-01", user_name="Alex Manager", role="owner")
        db.session.add(manager_membership)
        db.session.commit()
        return jsonify({"id": new_team.id, "name": new_team.name, "code": new_team.code, "memberCount": 1})

# ... all other routes would need to be updated to use the db session ...

# --- Command to create database tables ---
@application.cli.command("create-db")
def create_db_command():
    """Creates the database tables."""
    with application.app_context():
        db.create_all()
    print("Database tables created!")

if __name__ == '__main__':
    application.run(debug=True, port=8888)