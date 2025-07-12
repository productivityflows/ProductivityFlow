import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
import string

application = Flask(__name__)

# --- Database Configuration ---
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

# --- Database Models ---
class Team(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

# --- THIS DECORATOR IS THE FIX ---
@application.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, DELETE'
    return response
# --- END OF FIX ---

def generate_id(prefix):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

# --- API Routes ---
@application.route('/api/teams', methods=['POST', 'GET'])
def handle_teams():
    if request.method == 'GET':
        teams = Team.query.all()
        return jsonify({"teams": [{"id": t.id, "name": t.name, "code": t.code} for t in teams]})
    if request.method == 'POST':
        # ... logic for creating a team
        return jsonify({"message": "Team created"})

@application.route('/api/teams/join', methods=['POST'])
def join_team():
    # ... logic for joining a team
    return jsonify({"message": "Successfully joined team"})

# ... your other routes ...