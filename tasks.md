# aidocs Implementation Tasks

## bd: Set up uv project structure and dependencies
- label: infrastructure
- priority: p1
Create pyproject.toml with uv, click, sqlite dependencies. Set up src/aidocs package structure with __init__.py, cli.py, database.py, models.py, utils.py

## bd: Implement core database layer and models
- label: backend
- priority: p1
- blocks: aidocs-store-command
Create SQLite schema, Doc data class, database operations (create, read, update, search), version tracking, basic migrations

## bd: Build primary store command for AI doc creation
- label: backend
- priority: p1
- blocks: aidocs-search-show
Implement `aidocs store <name> <description> <content>` command with validation, conflict checking, version management

## bd: Implement search and show commands for doc discovery
- label: backend
- priority: p1
- blocks: aidocs-workflow-commands
Build `aidocs search <query>` with keyword matching and `aidocs show <name>` for reading docs

## bd: Create AI workflow commands (append, record_decision)
- label: backend
- priority: p2
- blocks: aidocs-testing
Implement `aidocs append` and `aidocs record_decision` for AI to update docs during work

## bd: Build comprehensive test suite
- label: testing
- priority: p2
- blocks: aidocs-integration
Create tests for all CLI commands, database operations, edge cases, mock scenarios

## bd: Create Claude Code skill documentation
- label: integration
- priority: p2
- blocks: aidocs-hooks
Write skill.md with AI workflow patterns, command examples, integration guide

## bd: Implement hooks configuration system
- label: integration
- priority: p2
- blocks: aidocs-testing-integration
Create hooks template, configuration loading, integration instructions

## bd: Test CLI on example project
- label: testing
- priority: p3
Create example project, test CLI commands, validate workflow with test scenarios

## bd: Test Claude Code integration end-to-end
- label: testing
- priority: p3
Test skills + hooks with actual Claude Code agent, validate AI workflow, fix integration issues