from flask import Flask, request, jsonify, make_response
import random
import string
from collections import Counter

application = Flask(__name__)

# --- CORS Handling ---
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Using a simple in-memory dictionary for a reliable deployment
DB = { "teams": {}, "memberships": {}, "activity": {} }

def generate_id(prefix, length=8):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=length))}"

def generate_team_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# --- API Routes ---
@application.route('/')
def health_check():
    return jsonify({"status": "healthy"}), 200

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

@application.route('/api/teams/<team_id>/members', methods=['GET'])
def get_team_members(team_id):
    members = DB['memberships'].get(team_id, [])
    return jsonify({"members": members})

# ... Add back other necessary routes like join_team, activity, etc. from our previous working version
@application.route('/api/teams/join', methods=['POST'])
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

@application.route('/api/activity', methods=['POST'])
def receive_activity():
    data = request.get_json()
    # Basic handling for demo
    print(f"Activity received for user: {data.get('userId')}")
    return jsonify({"message": "Activity received"})

if __name__ == '__main__':
    application.run(debug=True, port=8888)