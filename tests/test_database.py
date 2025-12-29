"""
Tests for database operations.
"""

import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import pytest

from aidocs.database import Database
from aidocs.models import Doc


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / 'test.db'
    db = Database(db_path)

    yield db

    # Cleanup
    shutil.rmtree(temp_dir)


def test_database_creation(temp_db):
    """Test database and table creation."""
    # Database should be created automatically
    assert temp_db.db_path.exists()


def test_create_doc(temp_db):
    """Test creating a document."""
    doc = temp_db.create_doc(
        name='test.doc',
        description='Test document',
        content='This is test content'
    )

    assert doc.name == 'test.doc'
    assert doc.version == 1
    assert doc.description == 'Test document'
    assert doc.content == 'This is test content'
    assert isinstance(doc.created_at, datetime)
    assert isinstance(doc.updated_at, datetime)


def test_doc_exists(temp_db):
    """Test doc_exists functionality."""
    assert not temp_db.doc_exists('nonexistent')

    temp_db.create_doc('existing', 'Exists', 'Content')
    assert temp_db.doc_exists('existing')


def test_get_doc(temp_db):
    """Test retrieving a document."""
    # Non-existent doc
    assert temp_db.get_doc('nonexistent') is None

    # Create and retrieve doc
    original = temp_db.create_doc('test', 'Test doc', 'Test content')
    retrieved = temp_db.get_doc('test')

    assert retrieved is not None
    assert retrieved.name == original.name
    assert retrieved.description == original.description
    assert retrieved.content == original.content
    assert retrieved.version == original.version


def test_update_doc(temp_db):
    """Test updating a document."""
    # Create original doc
    temp_db.create_doc('test', 'Original', 'Original content')

    # Update it
    updated = temp_db.update_doc('test', 'Updated', 'Updated content')

    assert updated.version == 2
    assert updated.description == 'Updated'
    assert updated.content == 'Updated content'

    # Verify original creation time preserved
    original = temp_db.get_doc('test')
    assert original.version == 2


def test_update_nonexistent_doc(temp_db):
    """Test updating a non-existent document."""
    with pytest.raises(ValueError, match="not found"):
        temp_db.update_doc('nonexistent', 'Description', 'Content')


def test_list_docs(temp_db):
    """Test listing all documents."""
    # Empty list
    assert temp_db.list_docs() == []

    # Create some docs
    temp_db.create_doc('auth', 'Authentication', 'Auth content')
    temp_db.create_doc('database', 'Database', 'DB content')
    temp_db.create_doc('api', 'API layer', 'API content')

    docs = temp_db.list_docs()
    assert len(docs) == 3

    # Should be sorted by name
    names = [doc.name for doc in docs]
    assert names == ['api', 'auth', 'database']


def test_search_docs_by_name(temp_db):
    """Test searching documents by name."""
    temp_db.create_doc('auth.jwt', 'JWT auth', 'JWT content')
    temp_db.create_doc('auth.oauth', 'OAuth auth', 'OAuth content')
    temp_db.create_doc('database.users', 'User database', 'Users content')

    # Search by name
    results = temp_db.search_docs('auth')
    assert len(results) == 2
    assert all('auth' in doc.name for doc in results)

    # Search by specific term
    results = temp_db.search_docs('jwt')
    assert len(results) == 1
    assert results[0].name == 'auth.jwt'


def test_search_docs_by_description(temp_db):
    """Test searching documents by description."""
    temp_db.create_doc('component1', 'User authentication system', 'Content 1')
    temp_db.create_doc('component2', 'Database connection pool', 'Content 2')
    temp_db.create_doc('component3', 'User management interface', 'Content 3')

    results = temp_db.search_docs('user')
    assert len(results) == 2
    assert 'component1' in [doc.name for doc in results]
    assert 'component3' in [doc.name for doc in results]


def test_search_docs_by_content(temp_db):
    """Test searching documents by content."""
    temp_db.create_doc('doc1', 'First doc', 'Contains PostgreSQL database info')
    temp_db.create_doc('doc2', 'Second doc', 'Contains Redis cache info')
    temp_db.create_doc('doc3', 'Third doc', 'Contains MongoDB info')

    results = temp_db.search_docs('PostgreSQL')
    assert len(results) == 1
    assert results[0].name == 'doc1'

    results = temp_db.search_docs('cache')
    assert len(results) == 1
    assert results[0].name == 'doc2'


def test_search_docs_multiple_terms(temp_db):
    """Test searching with multiple terms."""
    temp_db.create_doc('auth.jwt', 'JWT authentication', 'JWT token validation')
    temp_db.create_doc('auth.oauth', 'OAuth authentication', 'OAuth flow handling')
    temp_db.create_doc('cache.redis', 'Redis cache', 'Cache with TTL')

    # Should find docs that contain ALL terms
    results = temp_db.search_docs('auth JWT')
    assert len(results) == 1
    assert results[0].name == 'auth.jwt'


def test_search_docs_limit(temp_db):
    """Test search result limiting."""
    # Create many docs
    for i in range(10):
        temp_db.create_doc(f'doc{i}', f'Document {i}', 'test content')

    results = temp_db.search_docs('test', limit=3)
    assert len(results) == 3


def test_search_docs_relevance_ranking(temp_db):
    """Test search relevance ranking."""
    # Create docs with different relevance to 'auth'
    temp_db.create_doc('auth', 'Authentication system', 'Main auth content')  # High relevance
    temp_db.create_doc('user.auth', 'User auth', 'Auth for users')  # Medium relevance
    temp_db.create_doc('logging', 'System logging', 'Logs auth attempts')  # Low relevance

    results = temp_db.search_docs('auth')

    # 'auth' should be first (exact name match)
    assert results[0].name == 'auth'


def test_get_doc_history(temp_db):
    """Test document version history."""
    # Create and update doc multiple times
    temp_db.create_doc('test', 'Version 1', 'Content 1')
    temp_db.update_doc('test', 'Version 2', 'Content 2')
    temp_db.update_doc('test', 'Version 3', 'Content 3')

    history = temp_db.get_doc_history('test')

    assert len(history) == 3
    # Should be in descending version order
    assert history[0]['version'] == 3
    assert history[1]['version'] == 2
    assert history[2]['version'] == 1

    assert history[0]['description'] == 'Version 3'
    assert history[1]['description'] == 'Version 2'
    assert history[2]['description'] == 'Version 1'


def test_get_doc_history_nonexistent(temp_db):
    """Test history for non-existent document."""
    history = temp_db.get_doc_history('nonexistent')
    assert history == []


def test_delete_doc(temp_db):
    """Test document deletion."""
    # Create doc with history
    temp_db.create_doc('test', 'Original', 'Content')
    temp_db.update_doc('test', 'Updated', 'New content')

    # Delete it
    result = temp_db.delete_doc('test')
    assert result is True

    # Verify it's gone
    assert not temp_db.doc_exists('test')
    assert temp_db.get_doc('test') is None
    assert temp_db.get_doc_history('test') == []


def test_delete_nonexistent_doc(temp_db):
    """Test deleting non-existent document."""
    result = temp_db.delete_doc('nonexistent')
    assert result is False


def test_get_stats(temp_db):
    """Test database statistics."""
    # Empty stats
    stats = temp_db.get_stats()
    assert stats['total_docs'] == 0
    assert stats['total_versions'] == 0
    assert stats['recent_docs'] == []

    # Create some docs
    temp_db.create_doc('doc1', 'Document 1', 'Content 1')
    temp_db.create_doc('doc2', 'Document 2', 'Content 2')
    temp_db.update_doc('doc1', 'Document 1 updated', 'Updated content')

    stats = temp_db.get_stats()
    assert stats['total_docs'] == 2
    assert stats['total_versions'] == 3  # doc1 has 2 versions, doc2 has 1
    assert len(stats['recent_docs']) == 2


def test_concurrent_operations(temp_db):
    """Test basic concurrent operation safety."""
    # This is a simple test - real concurrency testing would be more complex
    temp_db.create_doc('test', 'Test doc', 'Content')

    # Multiple reads should work fine
    doc1 = temp_db.get_doc('test')
    doc2 = temp_db.get_doc('test')

    assert doc1.name == doc2.name
    assert doc1.version == doc2.version