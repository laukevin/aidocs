# aidocs - AI-Native Architecture Documentation

> **Semantic grep for architecture** - A CLI tool designed for AI agents to store, search, and manage architecture documentation with git-based version history.

## What is aidocs?

`aidocs` solves the problem of AI agents having to rediscover architecture patterns every session. Instead of starting from scratch, AI agents can:

- **Search existing docs** before making changes
- **Store architectural findings** as they explore code
- **Record decisions** with rationale for future reference
- **Track documentation evolution** via git history

## How It Works

- Docs are stored as markdown files in `.aidocs/docs/`
- `.aidocs/` has its own git repo for version history (separate from your project)
- SQLite stores metadata index for fast search
- AI reads/edits files directly, then commits changes

---

## For Humans: Setup Guide

### Installation

```bash
# Install with uv (recommended)
uv tool install git+https://github.com/laukevin/aidocs.git

# Or with pip
pip install git+https://github.com/laukevin/aidocs.git
```

### Project Setup

Run this once in each repo where you want aidocs:

```bash
cd your-project
aidocs setup
```

This does three things:
1. Creates `.aidocs/` directory with its own git repo
2. Adds `.aidocs/` to `.gitignore` (never touches your main repo)
3. Installs Claude Code hooks for automatic context

Then **restart Claude Code**. The AI will automatically use aidocs during planning - you don't need to run commands manually.

### Verify Installation

```bash
aidocs doctor   # Check everything is configured
```

### Manual Usage (Optional)

While aidocs is designed for AI use, humans can also use it:

```bash
# See what's documented
aidocs list
aidocs search "authentication"

# Read a doc
aidocs show auth.overview
# Then open the file path shown

# Check status
aidocs status
```

---

## For AI Models: Usage Guide

### When to Use aidocs

| Phase | Action | Why |
|-------|--------|-----|
| **PLANNING/RESEARCH** | Read AND Write docs | Capture discoveries, create plans |
| **IMPLEMENTING** | Read docs only | Reference existing plans, don't create new docs |

### Core Workflow

#### Step 1: Search Before Working
```bash
aidocs search "<topic>"    # Search by name/description
aidocs list                # See all documented concepts
```

#### Step 2: Read a Doc
```bash
aidocs show <name>         # Returns file path
```
Then use your **Read tool** on that file path to view content.

#### Step 3: Create NEW Doc
If no relevant doc exists:
```bash
aidocs store <name> "<description>" "<initial content>"
```
Names use dot-hierarchy: `arch.overview`, `api.auth`, `plan.feature-x`

#### Step 4: Edit EXISTING Doc
```bash
aidocs show <name>                    # 1. Get file path
# Use Read tool to view               # 2. Read current content
# Use Edit tool to modify             # 3. Make targeted changes
aidocs commit <name> "<message>"      # 4. Commit with description
```

The commit message describes what changed. Git hash and date are recorded automatically.

### What to Document

**DO document:**
- Major architecture patterns and decisions
- Codebase layout and structure
- Implementation plans before starting work
- Key decisions with rationale

**DON'T document:**
- Small changes, constants, minor refactors
- Obvious implementation details
- Anything while actively implementing (read only)

### Command Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `search` | Find docs by keyword | `aidocs search "caching"` |
| `list` | List all docs | `aidocs list` |
| `show` | Get file path for reading | `aidocs show auth.jwt` |
| `store` | Create new doc | `aidocs store "api.users" "User API" "..."` |
| `commit` | Save changes to existing doc | `aidocs commit auth.jwt "Add rate limiting"` |
| `log` | View version history | `aidocs log auth.jwt` |
| `why` | Search past decisions | `aidocs why "database choice"` |

### Example Session

```bash
# Planning phase - exploring codebase
aidocs search "authentication"
# No results - need to document

aidocs store auth.overview "Authentication system overview" "# Auth Overview

## Components
- JWT tokens for API auth
- OAuth2 for social login
- Session middleware

## Key Files
- src/auth/jwt.py - Token generation
- src/auth/oauth.py - OAuth providers
"

# Later - updating the doc
aidocs show auth.overview
# Read tool: /path/to/.aidocs/docs/auth/overview.md
# Edit tool: Add new section about rate limiting
aidocs commit auth.overview "Add rate limiting documentation"

# Check history
aidocs log auth.overview
# Shows: hash | message | date for each version
```

---

## Architecture

### Storage Model

```
your-project/
├── .aidocs/              # Separate git repo
│   ├── .git/             # Version history for docs
│   ├── docs/             # Markdown files
│   │   ├── arch/
│   │   │   └── overview.md
│   │   └── api/
│   │       └── auth.md
│   └── store.db          # Metadata index (gitignored)
├── .gitignore            # Contains ".aidocs/"
└── ... your code ...
```

### Naming Conventions

Use hierarchical dot-notation:

```
arch.overview          # System architecture
auth.jwt               # JWT implementation
auth.oauth.google      # Google OAuth specifics
api.users              # User API endpoints
plan.feature-x         # Implementation plan
```

### Version History

Each doc change creates a git commit in `.aidocs/`:
- Commit message = your `aidocs commit` message
- Linked to main project's current commit hash
- View with `aidocs log <name>`

---

## Hooks & Integration

### Claude Code Hooks

After `aidocs setup`, these hooks are configured:

- **SessionStart**: Runs `aidocs prime` to inject documentation context
- **PreCompact**: Re-injects context before summarization

The `aidocs prime` command outputs nothing if `.aidocs/` doesn't exist, so it won't affect other projects.

### Manual Hook Management

```bash
aidocs install-hooks    # Add hooks to Claude Code
aidocs uninstall-hooks  # Remove hooks
aidocs doctor           # Verify configuration
```

---

## Development

### Running from Source

```bash
git clone https://github.com/anthropics/aidocs.git
cd aidocs
pip install -e .
```

### Project Structure

```
aidocs/
├── src/aidocs/
│   ├── cli.py          # Click CLI interface
│   ├── database.py     # SQLite + Git operations
│   └── models.py       # Data classes
├── tests/
└── examples/
```

## License

MIT License
