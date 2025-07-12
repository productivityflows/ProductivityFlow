import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import random
import string

application = Flask(__name__)

# --- Database Configuration ---
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

# --- THIS DECORATOR IS THE FIX ---
# It manually adds the required permission headers to every response
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# --- Database Models ---
class Team(db.Model):
    id = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)

# --- API Routes ---
@application.route('/')
def health_check():
    return jsonify({"status": "healthy"}), 200

@application.route('/api/teams', methods=['POST', 'GET'])
def handle_teams():
    # ... function code ...
    if request.method == 'GET':
        teams = Team.query.all()
        return jsonify({"teams": [{"id": t.id, "name": t.name, "code": t.code}]})
    if request.method == 'POST':
        data = request.get_json()
        team_id = f"team_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"
        new_team = Team(id=team_id, name=data['name'], code=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))
        db.session.add(new_team)
        db.session.commit()
        return jsonify({"id": new_team.id, "name": new_team.name, "code": new_team.code})

@application.route('/api/teams/join', methods=['POST'])
def join_team():
    # ... function code ...
    data = request.get_json()
    return jsonify({"message": f"Request to join with code {data.get('team_code')} received!"})


@application.cli.command("create-db")
def create_db_command():
    with application.app_context():
        db.create_all()
    print("Database tables created!")