# Installation Guide

## Quick Install (Recommended)

```bash
pip install aidocs
```

## Development Install

```bash
# Clone the repository
git clone https://github.com/anthropics/aidocs.git
cd aidocs

# Install in development mode
pip install -e .

# Or with uv (faster)
uv pip install -e .
```

## Install with All Features

```bash
# Install with development tools
pip install aidocs[dev]

# This includes: pytest, black, ruff, mypy for development
```

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, Windows
- **Dependencies**: None (SQLite is included with Python)

## Verify Installation

```bash
# Check that aidocs is installed
aidocs --version

# Initialize in a test directory
mkdir test-aidocs
cd test-aidocs
aidocs init

# Store a test document
aidocs store "test" "Test document" "This is a test of aidocs installation"

# Search for it
aidocs search "test"

# Success! aidocs is working
```

## Claude Code Integration

### 1. Install Claude Code Skill

```bash
# Copy the skill to your Claude Code skills directory
cp claude_code_integration/skill.md ~/.claude/skills/aidocs.md

# Or create a symbolic link for development
ln -s $(pwd)/claude_code_integration/skill.md ~/.claude/skills/aidocs.md
```

### 2. Enable Hooks (Optional)

Create `.aidocs/config.yaml` in your project:

```bash
# Copy the template
cp claude_code_integration/hooks_template.yaml .aidocs/config.yaml

# Customize as needed
```

### 3. Test Integration

Start Claude Code in a project with aidocs initialized:

```bash
cd your-project
aidocs init
claude  # Start Claude Code

# Claude will now have access to aidocs commands and workflow patterns
```

## Shell Completion

### Bash

```bash
# Add to ~/.bashrc
eval "$(_AIDOCS_COMPLETE=bash_source aidocs)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_AIDOCS_COMPLETE=zsh_source aidocs)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
eval (env _AIDOCS_COMPLETE=fish_source aidocs)
```

## Troubleshooting

### Permission Errors

```bash
# If you get permission errors on Linux/macOS
pip install --user aidocs

# Or use a virtual environment
python3 -m venv aidocs-env
source aidocs-env/bin/activate  # On Windows: aidocs-env\Scripts\activate
pip install aidocs
```

### Python Version Issues

```bash
# Check your Python version
python --version

# aidocs requires Python 3.8+
# On some systems, use python3 explicitly
python3 -m pip install aidocs
```

### SQLite Issues

aidocs uses SQLite which is included with Python. If you encounter database errors:

```bash
# Check SQLite is available
python3 -c "import sqlite3; print('SQLite version:', sqlite3.sqlite_version)"

# If missing, install Python with SQLite support
# On Ubuntu/Debian: apt install python3 python3-pip
# On macOS: Install Python from python.org
# On Windows: Download from python.org
```

### Claude Code Integration Issues

1. **Skill not found**: Ensure skill.md is in the correct skills directory
2. **Hooks not working**: Check `.aidocs/config.yaml` syntax with `yaml` validator
3. **Commands not found**: Verify aidocs is in PATH and accessible from Claude Code

## Uninstall

```bash
pip uninstall aidocs

# Remove configuration files if desired
rm -rf ~/.config/aidocs  # If any global config exists
```

## Development Setup

For contributing to aidocs:

```bash
# Clone and setup development environment
git clone https://github.com/anthropics/aidocs.git
cd aidocs

# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Check code style
black --check src/
ruff check src/

# Type checking
mypy src/aidocs/

# Build package
./scripts/build.sh
```

## Getting Help

- **Documentation**: See README.md and examples/
- **Issues**: https://github.com/anthropics/aidocs/issues
- **Commands**: `aidocs --help` or `aidocs <command> --help`
- **Examples**: Check examples/test_project/ for workflow demonstrations