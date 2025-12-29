"""
Tests for the CLI interface.
"""

import tempfile
import shutil
from pathlib import Path
from click.testing import CliRunner

import pytest

from aidocs.cli import cli
from aidocs.database import Database


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    original_cwd = Path.cwd()

    # Change to temp directory
    import os
    os.chdir(temp_dir)

    yield Path(temp_dir)

    # Cleanup
    os.chdir(original_cwd)
    shutil.rmtree(temp_dir)


@pytest.fixture
def runner():
    """Click test runner."""
    return CliRunner()


def test_init_command(temp_project_dir, runner):
    """Test aidocs init command."""
    result = runner.invoke(cli, ['init'])

    assert result.exit_code == 0
    assert "Initialized aidocs" in result.output

    # Check that .aidocs directory was created
    aidocs_dir = temp_project_dir / '.aidocs'
    assert aidocs_dir.exists()
    assert (aidocs_dir / 'store.db').exists()


def test_init_already_exists(temp_project_dir, runner):
    """Test init when already initialized."""
    # Initialize twice
    runner.invoke(cli, ['init'])
    result = runner.invoke(cli, ['init'])

    assert result.exit_code == 0
    assert "already initialized" in result.output


def test_store_command(temp_project_dir, runner):
    """Test basic store command."""
    runner.invoke(cli, ['init'])

    result = runner.invoke(cli, [
        'store',
        'auth.jwt',
        'JWT authentication system',
        'This handles JWT tokens for authentication.'
    ])

    assert result.exit_code == 0
    assert "Created doc: auth.jwt" in result.output


def test_store_invalid_name(temp_project_dir, runner):
    """Test store with invalid name."""
    runner.invoke(cli, ['init'])

    result = runner.invoke(cli, [
        'store',
        'Auth JWT',  # Invalid: has space
        'JWT authentication',
        'Content here'
    ])

    assert result.exit_code == 1
    assert "Invalid name" in result.output


def test_store_duplicate_without_update(temp_project_dir, runner):
    """Test storing duplicate without --update flag."""
    runner.invoke(cli, ['init'])

    # Create doc
    runner.invoke(cli, [
        'store', 'auth', 'Auth system', 'Auth content'
    ])

    # Try to create again without --update
    result = runner.invoke(cli, [
        'store', 'auth', 'Auth system updated', 'New content'
    ])

    assert result.exit_code == 1
    assert "already exists" in result.output


def test_store_update(temp_project_dir, runner):
    """Test updating existing doc."""
    runner.invoke(cli, ['init'])

    # Create doc
    runner.invoke(cli, [
        'store', 'auth', 'Auth system', 'Original content'
    ])

    # Update it
    result = runner.invoke(cli, [
        'store', 'auth', 'Updated auth system', 'New content', '--update'
    ])

    assert result.exit_code == 0
    assert "Updated doc: auth" in result.output


def test_show_command(temp_project_dir, runner):
    """Test show command."""
    runner.invoke(cli, ['init'])

    # Create and show doc
    runner.invoke(cli, [
        'store', 'database', 'Database layer', 'PostgreSQL with connection pooling'
    ])

    result = runner.invoke(cli, ['show', 'database'])

    assert result.exit_code == 0
    assert "database" in result.output
    assert "Database layer" in result.output
    assert "PostgreSQL" in result.output


def test_show_nonexistent(temp_project_dir, runner):
    """Test show for non-existent doc."""
    runner.invoke(cli, ['init'])

    result = runner.invoke(cli, ['show', 'nonexistent'])

    assert result.exit_code == 0
    assert "No doc found" in result.output


def test_search_command(temp_project_dir, runner):
    """Test search functionality."""
    runner.invoke(cli, ['init'])

    # Create some docs
    runner.invoke(cli, [
        'store', 'auth.jwt', 'JWT tokens', 'JWT authentication system'
    ])
    runner.invoke(cli, [
        'store', 'auth.oauth', 'OAuth2 flow', 'OAuth2 authentication flow'
    ])
    runner.invoke(cli, [
        'store', 'database', 'Database layer', 'PostgreSQL database'
    ])

    # Search for auth
    result = runner.invoke(cli, ['search', 'auth'])

    assert result.exit_code == 0
    assert "auth.jwt" in result.output
    assert "auth.oauth" in result.output
    assert "database" not in result.output  # Should not match


def test_search_no_results(temp_project_dir, runner):
    """Test search with no results."""
    runner.invoke(cli, ['init'])

    result = runner.invoke(cli, ['search', 'nonexistent'])

    assert result.exit_code == 0
    assert "No docs found" in result.output
    assert "aidocs store" in result.output  # Suggestion to create


def test_list_command(temp_project_dir, runner):
    """Test list command."""
    runner.invoke(cli, ['init'])

    # Create some docs
    runner.invoke(cli, [
        'store', 'auth', 'Authentication', 'Auth content'
    ])
    runner.invoke(cli, [
        'store', 'database', 'Database', 'DB content'
    ])

    result = runner.invoke(cli, ['list'])

    assert result.exit_code == 0
    assert "auth" in result.output
    assert "database" in result.output
    assert "Authentication" in result.output
    assert "Database" in result.output


def test_list_empty(temp_project_dir, runner):
    """Test list when no docs exist."""
    runner.invoke(cli, ['init'])

    result = runner.invoke(cli, ['list'])

    assert result.exit_code == 0
    assert "No documents found" in result.output


def test_list_tree(temp_project_dir, runner):
    """Test list with tree format."""
    runner.invoke(cli, ['init'])

    # Create hierarchical docs
    runner.invoke(cli, [
        'store', 'auth', 'Authentication', 'Top level auth'
    ])
    runner.invoke(cli, [
        'store', 'auth.jwt', 'JWT tokens', 'JWT implementation'
    ])
    runner.invoke(cli, [
        'store', 'auth.oauth', 'OAuth flow', 'OAuth implementation'
    ])

    result = runner.invoke(cli, ['list', '--tree'])

    assert result.exit_code == 0
    assert "auth/" in result.output
    assert "├──" in result.output or "└──" in result.output


def test_append_command(temp_project_dir, runner):
    """Test append command."""
    runner.invoke(cli, ['init'])

    # Create doc
    runner.invoke(cli, [
        'store', 'auth', 'Authentication', 'Original content'
    ])

    # Append to it
    result = runner.invoke(cli, [
        'append', 'auth', 'Added new feature', '--section', 'Recent Changes'
    ])

    assert result.exit_code == 0
    assert "Added to Recent Changes" in result.output

    # Verify content was added
    show_result = runner.invoke(cli, ['show', 'auth'])
    assert "Added new feature" in show_result.output


def test_record_decision_command(temp_project_dir, runner):
    """Test record_decision command."""
    runner.invoke(cli, ['init'])

    # Create doc
    runner.invoke(cli, [
        'store', 'auth', 'Authentication', 'Auth content'
    ])

    # Record a decision
    result = runner.invoke(cli, [
        'record_decision', 'auth', 'Token storage strategy', 'Use Redis for performance'
    ])

    assert result.exit_code == 0
    assert "Recorded decision" in result.output

    # Verify decision was added
    show_result = runner.invoke(cli, ['show', 'auth'])
    assert "Token storage strategy" in show_result.output
    assert "Use Redis for performance" in show_result.output


def test_log_command(temp_project_dir, runner):
    """Test log command for version history."""
    runner.invoke(cli, ['init'])

    # Create and update doc multiple times
    runner.invoke(cli, [
        'store', 'auth', 'Authentication v1', 'Version 1 content'
    ])
    runner.invoke(cli, [
        'store', 'auth', 'Authentication v2', 'Version 2 content', '--update'
    ])

    result = runner.invoke(cli, ['log', 'auth'])

    assert result.exit_code == 0
    assert "Version history" in result.output
    assert "Authentication v1" in result.output
    assert "Authentication v2" in result.output


def test_why_command(temp_project_dir, runner):
    """Test why command for decision search."""
    runner.invoke(cli, ['init'])

    # Create doc with decision
    content = """
    ## Decisions Made
    **Decision**: Database choice
    **Rationale**: PostgreSQL for ACID compliance
    """

    runner.invoke(cli, [
        'store', 'database', 'Database layer', content
    ])

    result = runner.invoke(cli, ['why', 'database'])

    assert result.exit_code == 0
    # Should find the decision content


def test_status_command(temp_project_dir, runner):
    """Test status command."""
    runner.invoke(cli, ['init'])

    # Create some docs
    runner.invoke(cli, [
        'store', 'auth', 'Authentication', 'Auth content'
    ])

    result = runner.invoke(cli, ['status'])

    assert result.exit_code == 0
    assert "aidocs Status" in result.output
    assert "Total documents: 1" in result.output


def test_workflow_end_to_end(temp_project_dir, runner):
    """Test complete AI workflow."""
    runner.invoke(cli, ['init'])

    # 1. Store initial documentation
    result1 = runner.invoke(cli, [
        'store',
        'auth.jwt',
        'JWT authentication middleware',
        'Handles JWT token validation for API requests'
    ])
    assert result1.exit_code == 0

    # 2. Search for it
    result2 = runner.invoke(cli, ['search', 'jwt'])
    assert result2.exit_code == 0
    assert 'auth.jwt' in result2.output

    # 3. Show the doc
    result3 = runner.invoke(cli, ['show', 'auth.jwt'])
    assert result3.exit_code == 0
    assert 'JWT authentication middleware' in result3.output

    # 4. Append progress
    result4 = runner.invoke(cli, [
        'append', 'auth.jwt', 'Implemented token blacklist feature'
    ])
    assert result4.exit_code == 0

    # 5. Record a decision
    result5 = runner.invoke(cli, [
        'record_decision',
        'auth.jwt',
        'Token expiration time',
        'Use 15 minutes for security balance'
    ])
    assert result5.exit_code == 0

    # 6. Update the doc
    result6 = runner.invoke(cli, [
        'store',
        'auth.jwt',
        'JWT authentication middleware with blacklist',
        'Enhanced JWT system with token blacklist and 15min expiration',
        '--update'
    ])
    assert result6.exit_code == 0

    # 7. Check version history
    result7 = runner.invoke(cli, ['log', 'auth.jwt'])
    assert result7.exit_code == 0
    assert 'Version history' in result7.output

    # 8. Search decisions
    result8 = runner.invoke(cli, ['why', 'token'])
    assert result8.exit_code == 0

    # 9. Final status check
    result9 = runner.invoke(cli, ['status'])
    assert result9.exit_code == 0
    assert 'Total documents: 1' in result9.output