# aidocs - AI-Native Architecture Documentation

## Overview
`aidocs` is a CLI tool designed specifically for AI agents to store, search, and manage architecture documentation. It provides semantic search, version history, and decision tracking—all optimized for AI workflows.

## Core Concept
AI agents use aidocs as external memory during development. Instead of rediscovering architecture patterns each time, agents can:
- Store findings as they explore codebases
- Search existing documentation before making changes
- Record architectural decisions with rationale
- Track documentation evolution over time

## Quick Commands Reference

| Need to... | Command |
|------------|---------|
| Find relevant docs | `aidocs search "<keywords>"` |
| Store new documentation | `aidocs store <name> "<description>" "<content>"` |
| Read a specific doc | `aidocs show <name>` |
| List all documented concepts | `aidocs list` |
| Add progress notes | `aidocs append <name> "<update>"` |
| Record a decision | `aidocs record-decision <name> "<decision>" "<rationale>"` |
| Search past decisions | `aidocs why "<query>"` |
| See project overview | `aidocs status` |
| View version history | `aidocs log <name>` |

## AI Workflow Patterns

### Pattern 1: Understanding Before Coding
When you encounter unfamiliar code or need to understand existing architecture:

```bash
# Search for related documentation
aidocs search "authentication"
aidocs search "database connection"
aidocs search "api middleware"

# Read specific documentation
aidocs show auth.jwt
aidocs show database.connection

# Check past architectural decisions
aidocs why "token expiration"
aidocs why "database choice"
```

### Pattern 2: Documenting Discoveries
As you explore and understand code, store your findings:

```bash
# Document what you learned about a system
aidocs store "auth.jwt.middleware" \
  "JWT validation middleware for Express routes" \
  "
## Current State
Located in src/auth/middleware.ts. Uses RS256 algorithm.

## Architecture
- Validates JWT tokens on every API request
- Extracts user info and adds to req.user
- Returns 401 for invalid tokens
- Uses Redis blacklist for revoked tokens

## Key Files
- src/auth/middleware.ts (main implementation)
- src/auth/tokens.js (token utilities)
- config/jwt.js (configuration)

## Testing
npm test src/auth/middleware.test.js
"
```

### Pattern 3: Recording Decisions During Development
When making architectural choices, record the decision and rationale:

```bash
# Record decisions as you make them
aidocs record-decision "cache.strategy" \
  "Cache invalidation approach" \
  "Chose TTL-based over event-driven because simpler to implement and debug"

aidocs record-decision "database.users" \
  "User password storage" \
  "Using bcrypt with 12 rounds - balance of security vs performance"
```

### Pattern 4: Updating Documentation During Work
As you make changes, keep documentation current:

```bash
# Add progress updates
aidocs append "auth.jwt" "Added token blacklist feature using Redis"
aidocs append "api.rate-limit" "Implemented per-user rate limiting"

# Update full documentation
aidocs store "cache.redis" \
  "Enhanced Redis caching with compression" \
  "Updated cache implementation with gzip compression..." \
  --update
```

## Document Naming Conventions

Use hierarchical naming with dots to organize concepts:

```bash
# Good examples
aidocs store "auth" "Authentication system overview" "..."
aidocs store "auth.jwt" "JWT token implementation" "..."
aidocs store "auth.jwt.middleware" "Express JWT middleware" "..."
aidocs store "database.users" "User data model and queries" "..."
aidocs store "api.v2.endpoints" "API v2 endpoint definitions" "..."

# Avoid
aidocs store "JWT Auth"  # No spaces
aidocs store "Auth_JWT"  # No underscores
aidocs store "auth."     # No trailing dots
```

## Search Strategies

aidocs uses keyword matching across names, descriptions, and content:

```bash
# Search by technology
aidocs search "redis"
aidocs search "postgresql"
aidocs search "express"

# Search by concept
aidocs search "authentication"
aidocs search "caching"
aidocs search "rate limiting"

# Search by file patterns
aidocs search "middleware"
aidocs search "model"
aidocs search "endpoint"

# Search for decisions
aidocs why "performance"
aidocs why "security"
aidocs why "database"
```

## Integration with Development Workflow

### Before Starting Work
```bash
# Understand existing architecture
aidocs search "<area-you're-working-on>"
aidocs show <relevant-concepts>
aidocs why "<related-decisions>"
```

### During Development
```bash
# Document new patterns you discover
aidocs store <new-concept> "<description>" "<content>"

# Record architectural decisions
aidocs record-decision <concept> "<decision>" "<rationale>"

# Add progress updates
aidocs append <concept> "<progress-update>"
```

### After Completing Work
```bash
# Update documentation with changes
aidocs store <concept> "<updated-description>" "<updated-content>" --update

# Document new concepts created
aidocs store <new-concept> "<description>" "<implementation-details>"
```

## Common Use Cases

### API Development
```bash
# Document API structure
aidocs store "api.structure" "REST API organization" "Express app with middleware..."

# Document specific endpoints
aidocs store "api.users.endpoints" "User CRUD endpoints" "/users GET,POST,PUT,DELETE..."

# Record API design decisions
aidocs record-decision "api.versioning" "URL vs header versioning" "URL versioning for clarity"
```

### Database Work
```bash
# Document schema
aidocs store "database.schema" "PostgreSQL schema design" "Users, posts, comments tables..."

# Document query patterns
aidocs store "database.queries.performance" "Optimized queries" "Indexes on user_id, created_at..."

# Record data decisions
aidocs record-decision "database.users" "Password vs OAuth only" "Support both for flexibility"
```

### Frontend Integration
```bash
# Document component architecture
aidocs store "frontend.components" "React component structure" "Atomic design with..."

# Document state management
aidocs store "frontend.state" "Redux state organization" "Feature-based reducers..."

# Record frontend decisions
aidocs record-decision "frontend.routing" "Client vs server routing" "Client-side for SPA experience"
```

## Best Practices

### 1. Search Before Creating
Always search first to avoid duplicate documentation:
```bash
aidocs search "auth"  # Before documenting auth
aidocs search "cache" # Before documenting caching
```

### 2. Use Descriptive Names
Names should be specific and hierarchical:
```bash
# Good
auth.jwt.validation
database.connection.pool
api.v2.users.endpoints

# Too generic
auth
database
api
```

### 3. Include Context in Content
Documentation should include:
- Current state description
- Key files and their purposes
- Dependencies and relationships
- Testing approaches
- Recent changes and decisions

### 4. Record Decisions Immediately
Don't wait—record decisions as you make them:
```bash
aidocs record-decision "performance.caching" \
  "Cache level choice" \
  "Application-level cache instead of CDN because we need real-time invalidation"
```

### 5. Keep Documentation Current
Update docs when you make significant changes:
```bash
aidocs store "existing.concept" \
  "Updated description" \
  "Updated content reflecting changes..." \
  --update
```

## Troubleshooting

### No Search Results
```bash
# Try broader terms
aidocs search "auth"      # instead of "authentication middleware"
aidocs search "database"  # instead of "postgresql connection"

# Check what's documented
aidocs list
```

### Creating vs Updating
```bash
# Create new documentation
aidocs store "new.concept" "Description" "Content"

# Update existing (will error if doesn't exist)
aidocs store "existing.concept" "New description" "New content" --update
```

### Finding Past Decisions
```bash
# Search decision content
aidocs why "token"
aidocs why "database"
aidocs why "performance"

# Check specific concept decisions
aidocs show auth.jwt  # Look for "Decisions Made" section
```

## Example Session

Here's a complete example of using aidocs during development:

```bash
# Starting work on user authentication
aidocs search "auth"
# No results - this is a new project

# Exploring the codebase, find authentication files
aidocs store "auth.system" \
  "User authentication system overview" \
  "
## Current State
JWT-based auth with Express middleware in src/auth/

## Architecture
- Login endpoint generates JWT tokens
- Middleware validates tokens on protected routes
- User sessions stored in Redis
- Passwords hashed with bcrypt

## Key Files
- src/auth/login.js (login endpoint)
- src/auth/middleware.js (JWT validation)
- src/models/User.js (user model)
"

# Implementing OAuth integration, record decision
aidocs record-decision "auth.oauth" \
  "OAuth provider choice" \
  "Google OAuth for initial launch - largest user base"

# Add progress update
aidocs append "auth.system" "Added Google OAuth integration"

# Complete OAuth work, update documentation
aidocs store "auth.oauth.google" \
  "Google OAuth integration" \
  "
## Current State
Google OAuth2 flow integrated with existing JWT system

## Architecture
- OAuth callback creates internal JWT token
- Existing middleware unchanged
- User profiles sync from Google API

## Configuration
CLIENT_ID and CLIENT_SECRET in environment
Callback URL: /auth/google/callback
"

# Later, searching for auth info
aidocs search "oauth"
# Results: auth.oauth.google, auth.system (mentions OAuth)

# Check past decisions
aidocs why "oauth"
# Shows decision about Google OAuth provider choice

# See all auth documentation
aidocs search "auth"
# Shows: auth.system, auth.oauth.google
```

This workflow demonstrates how aidocs becomes the AI's external memory, capturing architectural knowledge and decisions for reuse across development sessions.