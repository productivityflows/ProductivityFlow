import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS # Import the library
import random
import string
from collections import Counter

app = Flask(__name__)

# --- NEW CORS CONFIGURATION ---
# This uses the Flask-Cors library to handle all CORS requests automatically
CORS(app)
# --- END OF NEW CONFIGURATION ---

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models ...
# (Your database models like Team, Membership, etc., would go here)
# For our demo, we will continue using the in-memory dictionary.
DB = { "teams": {}, "memberships": {}, "activity": {} }

# Helper functions...
def generate_id(prefix, length=8):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=length))}"

def generate_team_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# --- API Routes ---

@app.route('/api/teams', methods=['POST', 'GET'])
def handle_teams():
    if request.method == 'GET':
        return jsonify({"teams": list(DB['teams'].values())})
    if request.method == 'POST':
        data = request.get_json()
        team_id = generate_id("team")
        new_team = { "id": team_id, "name": data['name'], "code": generate_team_code(), "memberCount": 1 }
        DB['teams'][team_id] = new_team
        DB['memberships'][team_id] = [{"userId": "manager-01", "name": "Alex Manager", "role": "owner"}]
        return jsonify(new_team)

@app.route('/api/teams/<team_id>/members', methods=['GET'])
def get_team_members(team_id):
    members = DB['memberships'].get(team_id, [])
    return jsonify({"members": members})

# ... all your other API routes like join_team, activity, summary, etc. ...
@app.route('/api/teams/join', methods=['POST'])
def join_team():
    data = request.get_json()
    user_name = data.get('name', 'New User')
    team_code = data.get('team_code')
    target_team = next((team for team in DB['teams'].values() if team['code'] == team_code), None)
    if not target_team: return jsonify({"error": "Invalid team code"}), 404
    
    user_id = generate_id("user") 
    DB['memberships'][target_team['id']].append({"userId": user_id, "name": user_name, "role": "member"})
    target_team['memberCount'] += 1
    
    response_data = {"teamId": target_team['id'], "teamName": target_team['name'], "userId": user_id, "userName": user_name}
    return jsonify(response_data)

@app.route('/api/activity', methods=['POST'])
def receive_activity():
    data = request.get_json()
    user_id = data.get('userId')
    if user_id:
        if user_id not in DB['activity']: DB['activity'][user_id] = []
        DB['activity'][user_id].extend(data.get('activities', []))
    return jsonify({"message": "Activity received"})

if __name__ == '__main__':
    app.run(debug=True, port=8888)