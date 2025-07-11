import os
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import random
import string

# The Flask object is now named 'application' to match what AWS expects
application = Flask(__name__)

# --- Database Configuration ---
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

# ... All your database models (Team, Membership, etc.) would go here ...

# --- CORS Handling ---
@application.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- API Routes (now using @application.route) ---

@application.route('/api/teams', methods=['GET'])
def get_teams():
    # This is a placeholder. In a real app, you'd query your database.
    return jsonify({"teams": [{"id": "team1", "name": "Live Test Team", "code": "LIVE123", "memberCount": 1}]})

# ... All your other routes would be updated to use @application.route ...

# This is the main entry point for Gunicorn on Elastic Beanstalk
if __name__ == '__main__':
    application.run(debug=True, port=8888)