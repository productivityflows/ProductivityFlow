from flask import Flask, request, jsonify, make_response
import random
import string

application = Flask(__name__)

# --- CORS Handling ---
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
    response.headers.add('Access-Control-Allow-Methods', "GET,POST,OPTIONS")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

DB = { "teams": {}, "memberships": {}, "activity": {} }

def generate_id(prefix):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

def generate_team_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# --- API Routes ---
@application.route('/api/teams', methods=['POST', 'GET', 'OPTIONS'])
def handle_teams():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    if request.method == 'GET':
        return _corsify_actual_response(jsonify({"teams": list(DB['teams'].values())}))
    if request.method == 'POST':
        data = request.get_json()
        team_id = generate_id("team")
        new_team = { "id": team_id, "name": data['name'], "code": generate_team_code(), "memberCount": 1 }
        DB['teams'][team_id] = new_team
        DB['memberships'][team_id] = [{"userId": "manager-01", "name": "Alex Manager", "role": "owner"}]
        return _corsify_actual_response(jsonify(new_team))

@application.route('/api/teams/join', methods=['POST', 'OPTIONS'])
def join_team():
    if request.method == 'OPTIONS':
        return _build_cors_preflight_response()
    data = request.get_json()
    team_code = data.get('team_code')
    user_name = data.get('name', 'New User')
    target_team = next((team for team in DB['teams'].values() if team['code'] == team_code), None)
    if not target_team:
        return _corsify_actual_response(jsonify({"error": "Invalid team code"})), 404

    user_id = generate_id("user")
    DB['memberships'][target_team['id']].append({"userId": user_id, "name": user_name, "role": "member"})
    target_team['memberCount'] += 1

    response_data = {"teamId": target_team['id'], "teamName": target_team['name'], "userId": user_id, "userName": user_name}
    return _corsify_actual_response(jsonify(response_data))

# All other routes should also handle OPTIONS if they accept POST/PUT etc.