"""
Data models for aidocs.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class Doc:
    """A documentation artifact."""

    name: str
    version: int
    description: str
    content: str
    created_at: datetime
    updated_at: datetime

    def __post_init__(self):
        """Validate the document after creation."""
        if not self.is_valid_name(self.name):
            raise ValueError(
                f"Invalid name '{self.name}'. Use lowercase with dots: 'auth.jwt.middleware'"
            )

        if not self.description.strip():
            raise ValueError("Description cannot be empty")

        if not self.content.strip():
            raise ValueError("Content cannot be empty")

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """
        Validate document name format.

        Rules:
        - Lowercase letters, numbers, dots, and hyphens only
        - Must start with a letter
        - Cannot end with a dot
        - No consecutive dots
        """
        if not name:
            return False

        pattern = r'^[a-z][a-z0-9.-]*[a-z0-9]$|^[a-z]$'
        if not re.match(pattern, name):
            return False

        # No consecutive dots
        if '..' in name:
            return False

        return True

    @property
    def hierarchy_parts(self) -> list[str]:
        """Get the hierarchical parts of the name."""
        return self.name.split('.')

    @property
    def parent_name(self) -> Optional[str]:
        """Get the parent document name if this is hierarchical."""
        parts = self.hierarchy_parts
        if len(parts) > 1:
            return '.'.join(parts[:-1])
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Doc':
        """Create Doc from dictionary."""
        return cls(
            name=data['name'],
            version=data['version'],
            description=data['description'],
            content=data['content'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
        )