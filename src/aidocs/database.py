"""
Database operations for aidocs.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from .models import Doc


class Database:
    """SQLite database manager for aidocs."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self) -> None:
        """Create database and tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main docs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS docs (
                    name TEXT PRIMARY KEY,
                    version INTEGER NOT NULL DEFAULT 1,
                    description TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Version history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS doc_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    description TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_docs_updated_at
                ON docs(updated_at DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_doc_versions_name_version
                ON doc_versions(name, version DESC)
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception:
            conn.rollback()
            raise
        else:
            conn.commit()
        finally:
            conn.close()

    def doc_exists(self, name: str) -> bool:
        """Check if a document exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM docs WHERE name = ?", (name,))
            return cursor.fetchone() is not None

    def create_doc(self, name: str, description: str, content: str) -> Doc:
        """Create a new document."""
        now = datetime.now()

        doc = Doc(
            name=name,
            version=1,
            description=description,
            content=content,
            created_at=now,
            updated_at=now,
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Insert into main table
            cursor.execute("""
                INSERT INTO docs (name, version, description, content, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                doc.name,
                doc.version,
                doc.description,
                doc.content,
                doc.created_at.isoformat(),
                doc.updated_at.isoformat(),
            ))

            # Insert into version history
            cursor.execute("""
                INSERT INTO doc_versions (name, version, description, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                doc.name,
                doc.version,
                doc.description,
                doc.content,
                doc.created_at.isoformat(),
            ))

        return doc

    def get_doc(self, name: str) -> Optional[Doc]:
        """Get a document by name."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, version, description, content, created_at, updated_at
                FROM docs WHERE name = ?
            """, (name,))

            row = cursor.fetchone()
            if not row:
                return None

            return Doc(
                name=row['name'],
                version=row['version'],
                description=row['description'],
                content=row['content'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
            )

    def update_doc(self, name: str, description: str, content: str) -> Doc:
        """Update an existing document."""
        existing = self.get_doc(name)
        if not existing:
            raise ValueError(f"Document '{name}' not found")

        now = datetime.now()
        new_version = existing.version + 1

        doc = Doc(
            name=name,
            version=new_version,
            description=description,
            content=content,
            created_at=existing.created_at,
            updated_at=now,
        )

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Update main table
            cursor.execute("""
                UPDATE docs
                SET version = ?, description = ?, content = ?, updated_at = ?
                WHERE name = ?
            """, (
                doc.version,
                doc.description,
                doc.content,
                doc.updated_at.isoformat(),
                doc.name,
            ))

            # Insert into version history
            cursor.execute("""
                INSERT INTO doc_versions (name, version, description, content, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                doc.name,
                doc.version,
                doc.description,
                doc.content,
                doc.updated_at.isoformat(),
            ))

        return doc

    def list_docs(self) -> List[Doc]:
        """Get all documents."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, version, description, content, created_at, updated_at
                FROM docs
                ORDER BY name
            """)

            docs = []
            for row in cursor.fetchall():
                docs.append(Doc(
                    name=row['name'],
                    version=row['version'],
                    description=row['description'],
                    content=row['content'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                ))

            return docs

    def search_docs(self, query: str, limit: int = 10) -> List[Doc]:
        """Search documents by keywords."""
        terms = query.lower().split()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic query for multiple search terms
            where_conditions = []
            params = []

            for term in terms:
                where_conditions.append("""
                    (LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(content) LIKE ?)
                """)
                params.extend([f"%{term}%", f"%{term}%", f"%{term}%"])

            where_clause = " AND ".join(where_conditions)

            # Calculate relevance score
            score_parts = []
            for term in terms:
                score_parts.append(f"""
                    (CASE WHEN LOWER(name) LIKE ? THEN 10 ELSE 0 END) +
                    (LENGTH(LOWER(description)) - LENGTH(REPLACE(LOWER(description), ?, ''))) +
                    (LENGTH(LOWER(content)) - LENGTH(REPLACE(LOWER(content), ?, ''))) / 10
                """)
                params.extend([f"%{term}%", term, term])

            score_clause = " + ".join(score_parts)

            query_sql = f"""
                SELECT name, version, description, content, created_at, updated_at,
                       ({score_clause}) as relevance_score
                FROM docs
                WHERE {where_clause}
                ORDER BY relevance_score DESC, name
                LIMIT ?
            """

            params.append(limit)
            cursor.execute(query_sql, params)

            docs = []
            for row in cursor.fetchall():
                docs.append(Doc(
                    name=row['name'],
                    version=row['version'],
                    description=row['description'],
                    content=row['content'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                ))

            return docs

    def get_doc_history(self, name: str) -> List[Dict[str, Any]]:
        """Get version history for a document."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, description, created_at
                FROM doc_versions
                WHERE name = ?
                ORDER BY version DESC
            """, (name,))

            history = []
            for row in cursor.fetchall():
                history.append({
                    'version': row['version'],
                    'description': row['description'],
                    'created_at': row['created_at'],
                })

            return history

    def delete_doc(self, name: str) -> bool:
        """Delete a document and its history."""
        if not self.doc_exists(name):
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DELETE FROM doc_versions WHERE name = ?", (name,))
            cursor.execute("DELETE FROM docs WHERE name = ?", (name,))

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM docs")
            total_docs = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM doc_versions")
            total_versions = cursor.fetchone()[0]

            cursor.execute("""
                SELECT name, updated_at
                FROM docs
                ORDER BY updated_at DESC
                LIMIT 5
            """)
            recent_docs = [
                {'name': row['name'], 'updated_at': row['updated_at']}
                for row in cursor.fetchall()
            ]

            return {
                'total_docs': total_docs,
                'total_versions': total_versions,
                'recent_docs': recent_docs,
            }