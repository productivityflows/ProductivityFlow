import os
from flask import Flask, request, jsonify, make_response
# We are not using SQLAlchemy for this simple version, so it's removed.
import random
import string

# The Flask object is now named 'application' to match what AWS expects
application = Flask(__name__)

# --- In-memory DB for our live demo ---
DB = { "teams": {}, "memberships": {}, "activity": {} }

# --- CORS Handling ---
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Helper functions
def generate_id(prefix, length=8):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=length))}"

def generate_team_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# --- API Routes ---
@application.route('/api/teams', methods=['POST', 'GET'])
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

# (Add back other routes as needed from previous versions)

# This is the main entry point for Gunicorn on Elastic Beanstalk
if __name__ == '__main__':
    application.run(debug=True, port=8888)