from flask import Flask, request, jsonify, make_response
import random
import string

application = Flask(__name__)

# --- CORS Handling ---
# This decorator will attach the necessary headers to every response
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

# --- In-memory Database ---
DB = { "teams": {}, "memberships": {} }

def generate_id(prefix):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- API Routes ---

@application.route('/api/teams', methods=['POST', 'GET', 'OPTIONS'])
def handle_teams():
    if request.method == 'OPTIONS':
        return make_response("OK", 200) # Handle pre-flight request
    if request.method == 'GET':
        return jsonify({"teams": list(DB['teams'].values())})
    if request.method == 'POST':
        data = request.get_json()
        team_id = generate_id("team")
        new_team = { "id": team_id, "name": data['name'], "code": generate_team_code(), "memberCount": 1 }
        DB['teams'][team_id] = new_team
        DB['memberships'][team_id] = [{"userId": "manager-01", "name": "Alex Manager", "role": "owner"}]
        return jsonify(new_team)

@application.route('/api/teams/join', methods=['POST', 'OPTIONS'])
def join_team():
    if request.method == 'OPTIONS':
        return make_response("OK", 200) # Handle pre-flight request

    data = request.get_json()
    user_name = data.get('name', 'New User')
    team_code = data.get('team_code')
    target_team = next((team for team in DB['teams'].values() if team['code'] == team_code), None)

    if not target_team:
        return jsonify({"error": "Invalid team code"}), 404

    user_id = generate_id("user")
    DB['memberships'][target_team['id']].append({"userId": user_id, "name": user_name, "role": "member"})
    target_team['memberCount'] += 1

    response_data = {"teamId": target_team['id'], "teamName": target_team['name'], "userId": user_id, "userName": user_name}
    return jsonify(response_data)