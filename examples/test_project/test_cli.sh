#!/bin/bash

# Test script for aidocs CLI
set -e

cd /data/projects/aidocs/examples/test_project
export PYTHONPATH="/data/projects/aidocs/src"

# Helper function to run aidocs commands
aidocs() {
    python3 -m aidocs.cli "$@"
}

echo "=== Testing aidocs CLI on example project ==="

echo "1. Testing init command..."
aidocs init

echo "2. Testing store command..."
aidocs store "auth.manager" "Authentication management system" "The AuthManager class handles user authentication and registration. It stores users in a simple dictionary and provides login/register methods."

echo "3. Testing store command with hierarchical naming..."
aidocs store "api.endpoints" "REST API endpoints" "The Flask API provides three main endpoints: GET /api/users (list users), POST /api/login (authenticate), POST /api/register (create user)."

echo "4. Testing list command..."
aidocs list

echo "5. Testing search command..."
aidocs search "authentication"

echo "6. Testing show command..."
aidocs show "auth.manager"

echo "7. Testing append command..."
aidocs append "auth.manager" "**Security Notes**: This is a mock implementation. In production, passwords should be hashed using bcrypt or similar."

echo "8. Testing record-decision command..."
aidocs record-decision "auth.manager" "Use dictionary storage for MVP" "Simple dictionary storage is sufficient for testing and MVP. Will migrate to database in production."

echo "9. Testing log command..."
aidocs log "auth.manager"

echo "10. Testing why command..."
aidocs why "dictionary"

echo "11. Testing status command..."
aidocs status

echo "12. Testing list with tree view..."
aidocs list --tree

echo "=== All CLI tests completed successfully! ==="