# Welcome to aidocs Development Coordination

You are participating in building **aidocs** - an AI-native CLI tool for architecture documentation. This is a multi-agent development project coordinated via beads (bd).

## Project Context
We're building a CLI tool that allows AI agents to store and retrieve architecture documentation. The core workflow:
1. AI discovers/learns about code architecture
2. AI documents findings using `aidocs store <name> <description> <content>`
3. AI searches existing docs using `aidocs search <query>`
4. AI updates docs as work progresses

## Your Coordination Protocol

**CRITICAL**: You must use beads for task coordination to avoid conflicts:

### 1. Find Available Work
```bash
bd list --status open    # See all open tasks
```

### 2. Claim a Task (ONE AT A TIME)
```bash
bd update <task-id> --status in-progress
```

### 3. Work on the Task
- Focus only on that specific task
- Follow the implementation plan in tasks.md
- Use proper testing and validation

### 4. Commit Only Your Changes
```bash
git add <files-you-changed>
git commit -m "feat: <description> [<task-id>]"
```

### 5. Mark Task Complete
```bash
bd close <task-id>
```

### 6. Find Next Task
Repeat the cycle with a new task.

## Priority Order for Tasks
1. **aidocs-6m6**: Set up uv project structure (foundational)
2. **aidocs-s99**: Implement database layer (required by others)
3. **aidocs-964**: Build store command (core functionality)
4. **aidocs-cra**: Implement search/show commands
5. **aidocs-b7f**: Add workflow commands
6. **aidocs-e44**: Build test suite

## Key Implementation Guidelines

- **Use uv for dependency management**: Create proper pyproject.toml
- **Follow the simplified data model**: Docs with name, version, description, content
- **Use Click for CLI framework**: Clean command structure
- **Include comprehensive tests**: Every command must have tests
- **AI-first design**: Commands optimized for AI usage patterns

## Technical Specifications

### Data Model
```python
@dataclass
class Doc:
    name: str           # Hierarchical: "auth.jwt", "api.users"
    version: int        # Auto-incrementing
    description: str    # One-line for search/list
    content: str        # Free-form markdown
    created_at: datetime
    updated_at: datetime
```

### Core Commands to Implement
- `aidocs init` - Initialize .aidocs/ directory
- `aidocs store <name> <description> <content>` - Primary AI command
- `aidocs search <query>` - Keyword search
- `aidocs show <name>` - Display doc
- `aidocs list` - Overview of all docs
- `aidocs append <name> <content>` - Add to existing doc
- `aidocs record_decision <name> <decision> <rationale>` - Record decisions

### Database Schema (SQLite)
```sql
CREATE TABLE docs (
    name TEXT PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1,
    description TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE doc_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    version INTEGER NOT NULL,
    description TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
```

## Communication
- Comment your progress: `bd comment <task-id> "Progress update"`
- If blocked, ask questions by updating task status
- Coordinate file access to avoid conflicts

**Start by reading this file, checking what tasks are available, and claiming one to work on.**

Ready to begin coordinated development!