#!/usr/bin/env python3
"""
Test aidocs workflow on the example project.
This simulates how an AI agent would use aidocs while exploring and documenting a codebase.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

# Add parent aidocs to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from aidocs.cli import cli
from click.testing import CliRunner


def run_aidocs_workflow():
    """Simulate AI agent documenting the example project."""
    print("🚀 Testing aidocs on example project...")

    # Change to example project directory
    project_dir = Path(__file__).parent
    original_cwd = Path.cwd()
    os.chdir(project_dir)

    runner = CliRunner()

    try:
        # Step 1: Initialize aidocs
        print("\n📋 Step 1: Initialize aidocs")
        result = runner.invoke(cli, ['init'])
        print(f"   Status: {result.exit_code}")
        print(f"   Output: {result.output.strip()[:100]}...")
        assert result.exit_code == 0

        # Step 2: Document overall architecture
        print("\n🏗️  Step 2: Document overall architecture")
        result = runner.invoke(cli, [
            'store', 'architecture',
            'Express.js REST API with JWT authentication',
            '''
## Current State
Node.js Express application with JWT-based authentication and PostgreSQL database.

## Architecture
- Express.js web framework
- JWT tokens for authentication (15min expiration)
- Redis for token blacklist
- PostgreSQL for user data
- bcrypt for password hashing (12 rounds)

## Key Files
- src/app.js: Main application and middleware setup
- src/auth/: Authentication system
- src/api/: API endpoints
- src/database/: Database layer

## Dependencies
- express: Web framework
- jsonwebtoken: JWT handling
- bcrypt: Password hashing
- redis: Token blacklist
- pg: PostgreSQL client

## Security Model
- JWT tokens with 15-minute expiration
- Token blacklist for logout/revocation
- bcrypt with 12 rounds for passwords
- Authorization header: Bearer <token>
            '''
        ])
        print(f"   Status: {result.exit_code}")
        assert result.exit_code == 0

        # Step 3: Document authentication system
        print("\n🔐 Step 3: Document authentication system")
        result = runner.invoke(cli, [
            'store', 'auth.system',
            'JWT-based authentication with token blacklist',
            '''
## Current State
Complete JWT authentication system with registration, login, logout, and middleware protection.

## Architecture
Three main components:
1. **Authentication Routes** (src/auth/routes.js)
   - POST /auth/register: User registration with bcrypt
   - POST /auth/login: JWT token generation
   - POST /auth/logout: Token blacklist

2. **Authentication Middleware** (src/auth/middleware.js)
   - JWT token validation
   - Blacklist checking via Redis
   - User context injection (req.user)

3. **Security Features**
   - Password hashing: bcrypt with 12 rounds
   - Token expiration: 15 minutes
   - Token revocation: Redis blacklist
   - Input validation

## Token Structure
```json
{
  "userId": 123,
  "email": "user@example.com",
  "roles": ["user"],
  "exp": 1640995200
}
```

## Error Handling
- 401: Missing/invalid/expired tokens
- 409: User already exists
- 500: Server errors with logging
            '''
        ])
        print(f"   Status: {result.exit_code}")
        assert result.exit_code == 0

        # Step 4: Record a key decision
        print("\n💡 Step 4: Record architectural decision")
        result = runner.invoke(cli, [
            'record-decision', 'auth.system',
            'JWT token expiration time',
            'Chose 15 minutes as balance between security and user experience - short enough for security but not too frequent re-auth'
        ])
        print(f"   Status: {result.exit_code}")
        assert result.exit_code == 0

        # Step 5: Document JWT middleware specifically
        print("\n🛡️  Step 5: Document JWT middleware")
        result = runner.invoke(cli, [
            'store', 'auth.jwt.middleware',
            'Express middleware for JWT token validation',
            '''
## Current State
Express middleware that validates JWT tokens and protects routes.

## Function Flow
1. Extract token from Authorization header (Bearer format)
2. Check token against Redis blacklist
3. Verify JWT signature and expiration
4. Add user context to req.user
5. Call next() or return error

## Error Responses
- 401: "Access token required" - no token provided
- 401: "Token has been revoked" - token blacklisted
- 401: "Token expired" - token past expiration
- 401: "Invalid token" - signature/format invalid
- 500: Redis connection or verification errors

## Usage Pattern
```javascript
// Protect all API routes
app.use('/api', authenticateToken, apiRoutes);

// Access user in protected route
app.get('/api/profile', (req, res) => {
  const userId = req.user.userId; // Available after middleware
});
```

## Dependencies
- jsonwebtoken: Token verification
- redis: Blacklist checking
- Environment: JWT_SECRET for signing key
            '''
        ])
        print(f"   Status: {result.exit_code}")
        assert result.exit_code == 0

        # Step 6: Search for authentication docs
        print("\n🔍 Step 6: Search existing documentation")
        result = runner.invoke(cli, ['search', 'auth'])
        print(f"   Status: {result.exit_code}")
        print(f"   Results: Found {result.output.count('auth.')} auth-related docs")
        assert result.exit_code == 0
        assert 'auth.system' in result.output or 'architecture' in result.output  # Should find something with auth

        # Step 7: Add progress update
        print("\n📝 Step 7: Add progress update")
        result = runner.invoke(cli, [
            'append', 'auth.system',
            'Completed documentation of core authentication flow and middleware'
        ])
        print(f"   Status: {result.exit_code}")
        assert result.exit_code == 0

        # Step 8: Check what we've documented
        print("\n📊 Step 8: Review all documentation")
        result = runner.invoke(cli, ['list'])
        print(f"   Status: {result.exit_code}")
        doc_count = result.output.count('│')  # Count table rows
        print(f"   Documented concepts: {doc_count - 1}")  # Minus header
        assert result.exit_code == 0

        # Step 9: Show specific documentation
        print("\n👁️  Step 9: Show JWT middleware documentation")
        result = runner.invoke(cli, ['show', 'auth.jwt.middleware'])
        print(f"   Status: {result.exit_code}")
        print(f"   Content preview: {len(result.output)} characters")
        assert result.exit_code == 0
        assert 'Express middleware' in result.output

        # Step 10: Search for past decisions
        print("\n🤔 Step 10: Search architectural decisions")
        result = runner.invoke(cli, ['why', 'token expiration'])
        print(f"   Status: {result.exit_code}")
        print(f"   Found decision info: {'15 minutes' in result.output}")
        assert result.exit_code == 0

        # Step 11: Check project status
        print("\n📈 Step 11: Check project status")
        result = runner.invoke(cli, ['status'])
        print(f"   Status: {result.exit_code}")
        print(f"   Summary: {result.output.split('📚')[1].split('📝')[0].strip() if '📚' in result.output else 'Stats unavailable'}")
        assert result.exit_code == 0

        print("\n🎉 aidocs workflow test completed successfully!")
        print("\nWorkflow demonstrated:")
        print("  ✅ Initializing aidocs in a project")
        print("  ✅ Documenting overall architecture")
        print("  ✅ Documenting specific subsystems")
        print("  ✅ Recording architectural decisions")
        print("  ✅ Searching existing documentation")
        print("  ✅ Adding progress updates")
        print("  ✅ Reviewing all documentation")
        print("  ✅ Searching past decisions")

        return True

    except Exception as e:
        print(f"\n❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        os.chdir(original_cwd)
        # Cleanup .aidocs directory
        aidocs_dir = project_dir / '.aidocs'
        if aidocs_dir.exists():
            shutil.rmtree(aidocs_dir)


if __name__ == '__main__':
    success = run_aidocs_workflow()
    print(f"\n{'🟢 SUCCESS' if success else '🔴 FAILED'}: aidocs workflow test")
    sys.exit(0 if success else 1)