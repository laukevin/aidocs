# aidocs - AI-Native Architecture Documentation

> **Semantic grep for architecture** - A CLI tool designed for AI agents to store, search, and manage architecture documentation.

## Overview

`aidocs` solves the problem of AI agents having to rediscover architecture patterns every time they work on a codebase. Instead of starting from scratch, AI agents can:

- 🔍 **Search existing documentation** before making changes
- 📝 **Store architectural findings** as they explore code
- 🎯 **Record decisions** with rationale for future reference
- 📈 **Track documentation evolution** over time

## Key Features

- **AI-Optimized**: Commands designed for AI workflow patterns
- **Semantic Search**: Find relevant docs by keywords, not exact names
- **Version History**: Track how architecture evolves over time
- **Decision Tracking**: Record architectural decisions with rationale
- **Hierarchical Organization**: Use dotted names like `auth.jwt.middleware`
- **Local Storage**: Everything stored in `.aidocs/` - no external dependencies

## Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd aidocs

# Install with uv (recommended)
uv pip install -e .

# Or with pip
pip install -e .
```

### Basic Usage

```bash
# Initialize in your project
aidocs init

# Store architecture documentation
aidocs store "auth.jwt" \
  "JWT authentication system" \
  "Handles token generation and validation for API authentication..."

# Search for documentation
aidocs search "authentication"
aidocs search "jwt tokens"

# Read specific documentation
aidocs show auth.jwt

# List all documented concepts
aidocs list

# Record architectural decisions
aidocs record-decision "auth.jwt" \
  "Token expiration strategy" \
  "15-minute expiration for security vs usability balance"
```

## Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `aidocs init` | Initialize .aidocs/ directory | `aidocs init` |
| `aidocs store` | Create/update documentation | `aidocs store "api.users" "User endpoints" "REST API for user operations..."` |
| `aidocs search` | Find relevant documentation | `aidocs search "caching"` |
| `aidocs show` | Display specific documentation | `aidocs show auth.jwt` |
| `aidocs list` | Overview of all concepts | `aidocs list` or `aidocs list --tree` |
| `aidocs append` | Add notes to existing docs | `aidocs append "api.users" "Added pagination support"` |
| `aidocs record-decision` | Record architectural decisions | `aidocs record-decision "database" "PostgreSQL vs MongoDB" "ACID compliance needed"` |
| `aidocs why` | Search past decisions | `aidocs why "database choice"` |
| `aidocs log` | View version history | `aidocs log auth.jwt` |
| `aidocs status` | Project overview | `aidocs status` |

## AI Workflow Integration

### Claude Code Integration

1. **Add the skill**: Copy `claude_code_integration/skill.md` to your Claude Code skills directory
2. **Install hooks**: Copy `claude_code_integration/hooks_template.yaml` to `.aidocs/config.yaml` in your project
3. **Start using**: Claude will be prompted to use aidocs at key moments

### Typical AI Workflow

```bash
# 1. Before working - understand existing architecture
aidocs search "authentication"
aidocs show auth.system
aidocs why "token strategy"

# 2. During work - document discoveries
aidocs store "auth.oauth.google" \
  "Google OAuth integration" \
  "OAuth2 flow with JWT token generation..."

# 3. Record decisions
aidocs record-decision "auth.oauth" \
  "OAuth provider choice" \
  "Google first - largest user base"

# 4. Update progress
aidocs append "auth.oauth.google" "Integration completed, tests passing"

# 5. Final documentation update
aidocs store "auth.oauth.google" \
  "Google OAuth integration (production ready)" \
  "Complete OAuth2 implementation with error handling..." \
  --update
```

## Document Organization

### Naming Conventions

Use hierarchical naming with dots:

```bash
# System overviews
auth                    # Authentication system overview
database               # Database architecture overview
api                     # API structure overview

# Specific components
auth.jwt               # JWT implementation
auth.oauth             # OAuth integration
auth.middleware        # Authentication middleware

# Detailed implementations
auth.jwt.validation    # JWT validation logic
auth.oauth.google      # Google OAuth specifics
database.users.model   # User data model
```

### Document Structure

Documents follow a flexible markdown structure:

```markdown
# concept-name

## Description
Brief one-line description for search results

## Current State
How this works right now

## Architecture
Key components, patterns, dependencies

## Key Files
Important files and their roles

## Testing
How to verify this works

## Tools & Commands
Relevant commands, scripts, deployment info

## Recent Changes
What changed recently and when

## Decisions Made
Key decisions with rationale and dates

## Notes
Additional context, gotchas, future considerations
```

## Advanced Usage

### Search Strategies

```bash
# Technology-based search
aidocs search "redis"
aidocs search "postgresql"

# Concept-based search
aidocs search "rate limiting"
aidocs search "user authentication"

# Decision search
aidocs why "performance"
aidocs why "security model"

# File-pattern search
aidocs search "middleware"
aidocs search "model"
```

### Version History

```bash
# View document evolution
aidocs log auth.jwt

# Compare with previous versions (future feature)
aidocs diff auth.jwt
```

### Bulk Operations

```bash
# List with tree view
aidocs list --tree

# Search with content preview
aidocs search "caching" --show-content

# Export documentation (future feature)
aidocs export --format markdown
```

## Configuration

### Project Configuration

Create `.aidocs/config.yaml`:

```yaml
# See claude_code_integration/hooks_template.yaml for full options
hooks:
  before_code_analysis: |
    aidocs search "<relevant-keywords>"
    aidocs show <relevant-concept>
```

### Git Integration

Add to `.gitignore`:

```gitignore
# aidocs (local documentation)
.aidocs/
```

This keeps documentation local to each development environment, as it's designed to be personal AI memory rather than shared project documentation.

## Development

### Running Tests

```bash
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/

# Run manual CLI test
python test_cli_manual.py
```

### Project Structure

```
aidocs/
├── src/aidocs/          # Main package
│   ├── cli.py          # Click CLI interface
│   ├── database.py     # SQLite operations
│   ├── models.py       # Data classes
│   └── utils.py        # Utility functions
├── tests/              # Test suite
├── claude_code_integration/  # Claude Code files
│   ├── skill.md        # Claude Code skill documentation
│   └── hooks_template.yaml  # Hooks configuration
└── examples/           # Example projects
```

## Philosophy

### AI-First Design

aidocs is built specifically for AI agents:

- **Search-first interface**: AIs find docs by query, not memorized names
- **Contextual commands**: Commands match AI workflow patterns
- **Decision tracking**: Every "why" question gets an answer
- **Evolution awareness**: Documentation tracks how things change over time

### Local-First Approach

- **No external dependencies**: Just SQLite in `.aidocs/`
- **Version controlled**: Documentation evolves with code
- **Privacy-focused**: Stays on your machine
- **Fast access**: No network calls, instant search

### Semantic Organization

- **Hierarchical naming**: Natural organization with dots
- **Flexible structure**: Markdown content adapts to needs
- **Search-optimized**: Find docs by meaning, not exact terms
- **Cross-references**: Link concepts naturally

## Examples

### Web Application Documentation

```bash
# System architecture
aidocs store "architecture" "MERN stack web application" "React frontend, Express API, MongoDB database..."

# Frontend documentation
aidocs store "frontend.react" "React component architecture" "Feature-based organization with shared components..."
aidocs store "frontend.state" "Redux state management" "Normalized state with feature-based reducers..."

# Backend documentation
aidocs store "backend.api" "Express REST API" "RESTful endpoints with JWT authentication..."
aidocs store "backend.database" "MongoDB data layer" "User and content collections with relationships..."

# Infrastructure
aidocs store "deploy.docker" "Docker containerization" "Multi-stage build with nginx proxy..."
```

### Microservices Documentation

```bash
# Service overview
aidocs store "services.overview" "Microservices architecture" "User, Content, and Analytics services..."

# Individual services
aidocs store "services.user" "User management service" "Authentication, profiles, preferences..."
aidocs store "services.content" "Content management service" "CRUD operations for articles and media..."

# Inter-service communication
aidocs store "services.communication" "Service mesh with gRPC" "Protocol buffers for type-safe communication..."

# Deployment
aidocs store "deploy.kubernetes" "K8s deployment" "Helm charts with service discovery..."
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.