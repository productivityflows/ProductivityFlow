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
    # Add other fields as needed

class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(80), nullable=False)
    user_id = db.Column(db.String(80), nullable=False)
    user_name = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)

# --- API Routes ---
@application.route('/api/teams', methods=['POST', 'GET'])
def handle_teams():
    # This route will now work AFTER the db is initialized
    if request.method == 'GET':
        teams = Team.query.all()
        return jsonify({"teams": [{"id": t.id, "name": t.name, "code": t.code} for t in teams]})
    if request.method == 'POST':
        # ... POST logic here ...
        return jsonify({"message": "Team created"})

# ... Your other API routes ...

# --- NEW: Manual Database Setup Route ---
@application.route('/api/init-db', methods=['POST'])
def init_db():
    """A special endpoint to be called only once to create tables."""
    try:
        with application.app_context():
            db.create_all()
        return jsonify({"message": "Database tables created successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500