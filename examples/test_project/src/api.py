"""
API module for the test project.
"""

from flask import Flask, jsonify, request
from auth import AuthManager

app = Flask(__name__)
auth_manager = AuthManager()

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users."""
    return jsonify({"users": list(auth_manager.users.keys())})

@app.route('/api/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if auth_manager.login(username, password):
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    """Register endpoint."""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if auth_manager.register(username, password):
        return jsonify({"success": True, "message": "User registered"})
    else:
        return jsonify({"success": False, "message": "User already exists"}), 409

if __name__ == '__main__':
    app.run(debug=True)