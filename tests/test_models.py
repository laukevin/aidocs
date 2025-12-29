"""
Tests for data models.
"""

from datetime import datetime

import pytest

from aidocs.models import Doc


def test_doc_creation():
    """Test basic Doc creation."""
    now = datetime.now()
    doc = Doc(
        name='test.doc',
        version=1,
        description='Test document',
        content='This is test content',
        created_at=now,
        updated_at=now
    )

    assert doc.name == 'test.doc'
    assert doc.version == 1
    assert doc.description == 'Test document'
    assert doc.content == 'This is test content'
    assert doc.created_at == now
    assert doc.updated_at == now


def test_doc_validation_valid_names():
    """Test valid name validation."""
    valid_names = [
        'auth',
        'auth.jwt',
        'auth.jwt.middleware',
        'api.v2',
        'database.models.user',
        'cache-redis',
        'frontend-react',
        'a',
        'test123',
    ]

    for name in valid_names:
        assert Doc.is_valid_name(name), f"'{name}' should be valid"


def test_doc_validation_invalid_names():
    """Test invalid name validation."""
    invalid_names = [
        '',  # Empty
        'Auth',  # Uppercase
        'auth jwt',  # Space
        'auth.',  # Ends with dot
        '.auth',  # Starts with dot
        'auth..jwt',  # Consecutive dots
        'auth/jwt',  # Invalid character
        'auth_jwt',  # Underscore not allowed
        'auth#jwt',  # Special character
        '123auth',  # Starts with number
    ]

    for name in invalid_names:
        assert not Doc.is_valid_name(name), f"'{name}' should be invalid"


def test_doc_post_init_validation():
    """Test __post_init__ validation."""
    now = datetime.now()

    # Valid doc should work
    doc = Doc(
        name='valid.name',
        version=1,
        description='Valid description',
        content='Valid content',
        created_at=now,
        updated_at=now
    )
    assert doc.name == 'valid.name'

    # Invalid name should raise error
    with pytest.raises(ValueError, match="Invalid name"):
        Doc(
            name='Invalid Name',  # Has space
            version=1,
            description='Description',
            content='Content',
            created_at=now,
            updated_at=now
        )

    # Empty description should raise error
    with pytest.raises(ValueError, match="Description cannot be empty"):
        Doc(
            name='valid.name',
            version=1,
            description='',
            content='Content',
            created_at=now,
            updated_at=now
        )

    # Empty content should raise error
    with pytest.raises(ValueError, match="Content cannot be empty"):
        Doc(
            name='valid.name',
            version=1,
            description='Description',
            content='',
            created_at=now,
            updated_at=now
        )


def test_hierarchy_parts():
    """Test hierarchy_parts property."""
    now = datetime.now()

    # Simple name
    doc = Doc('auth', 1, 'Auth', 'Content', now, now)
    assert doc.hierarchy_parts == ['auth']

    # Hierarchical name
    doc = Doc('auth.jwt.middleware', 1, 'JWT middleware', 'Content', now, now)
    assert doc.hierarchy_parts == ['auth', 'jwt', 'middleware']

    # Two levels
    doc = Doc('api.users', 1, 'User API', 'Content', now, now)
    assert doc.hierarchy_parts == ['api', 'users']


def test_parent_name():
    """Test parent_name property."""
    now = datetime.now()

    # No parent
    doc = Doc('auth', 1, 'Auth', 'Content', now, now)
    assert doc.parent_name is None

    # One level parent
    doc = Doc('auth.jwt', 1, 'JWT', 'Content', now, now)
    assert doc.parent_name == 'auth'

    # Multi-level parent
    doc = Doc('auth.jwt.middleware', 1, 'Middleware', 'Content', now, now)
    assert doc.parent_name == 'auth.jwt'

    # Deep hierarchy
    doc = Doc('api.v2.users.endpoints', 1, 'Endpoints', 'Content', now, now)
    assert doc.parent_name == 'api.v2.users'


def test_to_dict():
    """Test dictionary conversion."""
    created = datetime(2024, 1, 15, 10, 30, 0)
    updated = datetime(2024, 1, 15, 14, 45, 0)

    doc = Doc(
        name='test.doc',
        version=2,
        description='Test document',
        content='Test content here',
        created_at=created,
        updated_at=updated
    )

    result = doc.to_dict()

    expected = {
        'name': 'test.doc',
        'version': 2,
        'description': 'Test document',
        'content': 'Test content here',
        'created_at': '2024-01-15T10:30:00',
        'updated_at': '2024-01-15T14:45:00',
    }

    assert result == expected


def test_from_dict():
    """Test creation from dictionary."""
    data = {
        'name': 'test.doc',
        'version': 2,
        'description': 'Test document',
        'content': 'Test content here',
        'created_at': '2024-01-15T10:30:00',
        'updated_at': '2024-01-15T14:45:00',
    }

    doc = Doc.from_dict(data)

    assert doc.name == 'test.doc'
    assert doc.version == 2
    assert doc.description == 'Test document'
    assert doc.content == 'Test content here'
    assert doc.created_at == datetime(2024, 1, 15, 10, 30, 0)
    assert doc.updated_at == datetime(2024, 1, 15, 14, 45, 0)


def test_round_trip_dict_conversion():
    """Test that to_dict/from_dict are symmetric."""
    now = datetime.now()
    original = Doc(
        name='round.trip.test',
        version=3,
        description='Round trip test',
        content='Content for round trip testing',
        created_at=now,
        updated_at=now
    )

    # Convert to dict and back
    dict_data = original.to_dict()
    restored = Doc.from_dict(dict_data)

    # Should be identical
    assert restored.name == original.name
    assert restored.version == original.version
    assert restored.description == original.description
    assert restored.content == original.content
    # Note: datetime comparison might have microsecond differences,
    # so we compare the ISO format strings
    assert restored.created_at.isoformat() == original.created_at.isoformat()
    assert restored.updated_at.isoformat() == original.updated_at.isoformat()