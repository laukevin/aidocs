# New Agent Instructions - aidocs Project

You are joining an aidocs development project that uses beads for task coordination. This is a CLI tool for AI-native architecture documentation.

## Setup
1. You're in `/data/projects/aidocs`
2. Read `COORDINATION_INSTRUCTIONS.md` for full context
3. Use beads (bd) commands for task coordination
4. Current status: Core CLI is mostly implemented, needs completion

## Critical - Beads Coordination

**Before starting ANY work:**
```bash
cd /data/projects/aidocs
bd list --status open    # See available tasks
```

**Claim ONE task:**
```bash
bd update <task-id> --status in_progress
```

## Available Tasks (check with bd list first)
- `aidocs-s99`: Core database layer (may need completion)
- `aidocs-964`: Store command implementation
- `aidocs-cra`: Search/show commands
- `aidocs-b7f`: Workflow commands (append, record-decision)
- `aidocs-vhu`: Hooks configuration system
- `aidocs-1os`: CLI testing on example project
- `aidocs-04h`: Claude Code integration testing

**NOTE:** `aidocs-b3h` (Claude Code skill docs) is claimed by main agent, `aidocs-6m6` and `aidocs-e44` are complete.

## After Completing a Task
```bash
git add <files-you-changed>
git commit -m "feat: <description> [<task-id>]"
bd close <task-id>
```

## Project Status
- Core CLI commands are implemented and tested
- Database layer is working
- All main commands functional: init, store, search, show, list, append, record-decision, log, status
- Need to finish remaining integration tasks

## Start By
1. Check `bd list --status open`
2. Claim ONE task that's still open
3. Work on it without conflicts
4. The main agent is paused, so coordinate through beads only

**Focus on completing integration and testing tasks. Avoid working on files the main agent might touch!**