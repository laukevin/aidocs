# Changelog

All notable changes to aidocs will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-30

### Added
- Initial release of aidocs - AI-Native Architecture Documentation System
- Core CLI commands: init, store, search, show, list, append, record-decision, log, status
- SQLite-based storage with version history
- Hierarchical concept organization with dotted naming (auth.jwt.middleware)
- Semantic search across names, descriptions, and content
- Decision tracking with rationale recording
- Rich terminal output with tables and formatting
- Comprehensive test suite with pytest and manual tests
- Claude Code integration with skills and hooks
- Shell completion support for major commands
- Example project demonstrating AI workflow
- Complete documentation and usage guides

### Features
- **Search-first design**: AI agents find docs by meaning, not memorized names
- **Version tracking**: See how architecture evolves over time
- **Local-first**: No external dependencies, privacy-focused storage
- **AI-optimized commands**: Workflow patterns designed for AI agents
- **Decision recording**: Capture architectural choices with rationale
- **Hierarchical organization**: Natural concept grouping with dotted names

### Technical Details
- Click CLI framework with rich terminal output
- SQLite database with proper schema and migrations
- Comprehensive input validation and error handling
- Data models with hierarchy support
- Test coverage for all major functionality
- Python 3.8+ compatibility
- Zero external runtime dependencies

### Claude Code Integration
- Complete skill documentation for AI workflow patterns
- Hooks configuration for automatic AI prompting
- Example workflows and best practices
- Installation and setup guides