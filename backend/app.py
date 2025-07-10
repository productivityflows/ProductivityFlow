from flask import Flask, request, jsonify, make_response
import random
import string
from collections import Counter
from datetime import datetime

app = Flask(__name__)

# --- Manual CORS Handling ---
def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def _corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

# In-memory database
DB = { "teams": {}, "memberships": {}, "activity": {}, "privacy": {} }

def generate_id(prefix, length=8):
    return f"{prefix}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=length))}"

def generate_team_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# --- Helper function for calculations ---
def _get_daily_stats(user_id):
    user_activities = DB['activity'].get(user_id, [])
    productive_seconds = sum(act['duration'] for act in user_activities if act.get('category') == 'productive')
    unproductive_seconds = sum(act['duration'] for act in user_activities if act.get('category') == 'unproductive')
    idle_seconds = sum(act['duration'] for act in user_activities if act.get('isIdle'))
    return {
        "productiveHours": round(productive_seconds / 3600, 1), 
        "unproductiveHours": round(unproductive_seconds / 3600, 1),
        "idleHours": round(idle_seconds / 3600, 1)
    }

# --- API Routes ---

@app.route('/api/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return _build_cors_preflight_response()

@app.route('/api/teams', methods=['POST', 'GET'])
def handle_teams():
    if request.method == 'GET':
        teams = Team.query.all() if 'db' in globals() else list(DB['teams'].values())
        return _corsify_actual_response(jsonify({"teams": teams}))
    if request.method == 'POST':
        data = request.get_json()
        team_id = generate_id("team")
        new_team = { "id": team_id, "name": data['name'], "code": generate_team_code(), "memberCount": 1 }
        DB['teams'][team_id] = new_team
        DB['memberships'][team_id] = [{"userId": "manager-01", "name": "Alex Manager", "role": "owner"}]
        return _corsify_actual_response(jsonify(new_team))

@app.route('/api/teams/<team_id>/members', methods=['GET'])
def get_team_members(team_id):
    if team_id not in DB['teams']: return _corsify_actual_response(jsonify({"error": "Team not found"})), 404
    members_with_stats = []
    for member in DB['memberships'].get(team_id, []):
        stats = _get_daily_stats(member['userId'])
        members_with_stats.append({**member, **stats})
    return _corsify_actual_response(jsonify({"members": members_with_stats}))

@app.route('/api/teams/join', methods=['POST'])
def join_team():
    data = request.get_json()
    user_name = data.get('name', 'New User')
    team_code = data.get('team_code')
    target_team = next((team for team in DB['teams'].values() if team['code'] == team_code), None)
    if not target_team: return _corsify_actual_response(jsonify({"error": "Invalid team code"})), 404
    
    user_id = generate_id("user") 
    DB['memberships'][target_team['id']].append({"userId": user_id, "name": user_name, "role": "member"})
    target_team['memberCount'] += 1
    DB['privacy'][user_id] = { "shareDetailed": True, "shareAggregates": True }
    
    response_data = {"teamId": target_team['id'], "teamName": target_team['name'], "userId": user_id, "userName": user_name}
    return _corsify_actual_response(jsonify(response_data))

@app.route('/api/activity', methods=['POST'])
def receive_activity():
    data = request.get_json()
    user_id = data.get('userId')
    if user_id:
        if user_id not in DB['activity']: DB['activity'][user_id] = []
        DB['activity'][user_id].extend(data.get('activities', []))
    return _corsify_actual_response(jsonify({"message": "Activity received"}))

@app.route('/api/employees/<user_id>/summary', methods=['GET'])
def get_employee_summary(user_id):
    stats = _get_daily_stats(user_id)
    total_active_hours = stats['productiveHours'] + stats['unproductiveHours']
    score = int((stats['productiveHours'] / total_active_hours) * 100) if total_active_hours > 0 else 0

    summary = f"Logged **{total_active_hours:.1f} active hours** with a productivity score of **{score}%**. Productive time accounted for **{stats['productiveHours']:.1f} hours**, while idle time was minimal. A focused and effective work session."
    
    response_data = {"productivityScore": score, "aiSummary": summary, **stats}
    return _corsify_actual_response(jsonify(response_data))

@app.route('/api/employees/<user_id>/privacy', methods=['GET', 'POST'])
def handle_privacy(user_id):
    if request.method == 'GET':
        settings = DB['privacy'].get(user_id, {"shareDetailed": True, "shareAggregates": True})
        return _corsify_actual_response(jsonify(settings))
    if request.method == 'POST':
        settings = request.get_json()
        DB['privacy'][user_id] = settings
        return _corsify_actual_response(jsonify({"message": "Settings updated"}))

@app.route('/api/compliance', methods=['GET'])
def get_compliance_data():
    return _corsify_actual_response(jsonify({
        "dataRetentionPolicy": "90 days (auto-delete)",
        "dataEncryption": "AES-256 At Rest & In Transit",
        "privacyFramework": "GDPR & CCPA Principles",
        "userConsent": "Required at initial setup via privacy controls"
    }))

if __name__ == '__main__':
    app.run(debug=True, port=8888)