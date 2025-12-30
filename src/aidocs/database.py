"""
Database operations for aidocs.

Storage model:
- Docs are stored as markdown files in .aidocs/docs/<name>.md
- .aidocs/ is its own git repo for version history
- SQLite stores metadata index (name, description, current version)
- Git is the source of truth for content history
"""

import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager

from .models import Doc


class Database:
    """SQLite database manager for aidocs metadata. Git handles content versioning."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.aidocs_dir = db_path.parent
        self.docs_dir = self.aidocs_dir / 'docs'
        self._ensure_db_exists()
        self._ensure_git_repo()

    def _ensure_db_exists(self) -> None:
        """Create database and tables if they don't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Main docs table - metadata index only, content lives in git-tracked files
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS docs (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_docs_updated_at
                ON docs(updated_at DESC)
            """)

            conn.commit()

    def _ensure_git_repo(self) -> None:
        """Initialize git repo in .aidocs/ if not exists."""
        git_dir = self.aidocs_dir / '.git'
        if not git_dir.exists():
            subprocess.run(
                ['git', 'init'],
                cwd=self.aidocs_dir,
                capture_output=True
            )
            # Configure git identity for the aidocs repo
            subprocess.run(
                ['git', 'config', 'user.email', 'aidocs@localhost'],
                cwd=self.aidocs_dir,
                capture_output=True
            )
            subprocess.run(
                ['git', 'config', 'user.name', 'aidocs'],
                cwd=self.aidocs_dir,
                capture_output=True
            )
            # Create .gitignore to ignore the SQLite files
            gitignore = self.aidocs_dir / '.gitignore'
            gitignore.write_text("*.db\n*.db-journal\n")
            # Initial commit
            subprocess.run(
                ['git', 'add', '.gitignore'],
                cwd=self.aidocs_dir,
                capture_output=True
            )
            subprocess.run(
                ['git', 'commit', '-m', 'Initialize aidocs repository'],
                cwd=self.aidocs_dir,
                capture_output=True
            )

    def _git_commit(self, file_path: Path, message: str) -> Optional[str]:
        """Git add and commit a file. Returns commit hash or None on failure."""
        try:
            # Add the file
            subprocess.run(
                ['git', 'add', str(file_path.relative_to(self.aidocs_dir))],
                cwd=self.aidocs_dir,
                capture_output=True,
                check=True
            )
            # Commit with message
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.aidocs_dir,
                capture_output=True,
                check=True
            )
            # Get the commit hash
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=self.aidocs_dir,
                capture_output=True,
                check=True
            )
            return result.stdout.decode().strip()
        except subprocess.CalledProcessError:
            return None

    def _git_log(self, file_path: Path, limit: int = 10) -> List[Dict[str, str]]:
        """Get git log for a file."""
        try:
            result = subprocess.run(
                ['git', 'log', '--pretty=format:%h|%s|%ai', f'-{limit}', '--',
                 str(file_path.relative_to(self.aidocs_dir))],
                cwd=self.aidocs_dir,
                capture_output=True,
                check=True
            )
            logs = []
            for line in result.stdout.decode().strip().split('\n'):
                if line:
                    parts = line.split('|', 2)
                    if len(parts) == 3:
                        logs.append({
                            'hash': parts[0],
                            'message': parts[1],
                            'date': parts[2]
                        })
            return logs
        except subprocess.CalledProcessError:
            return []

    def _get_main_repo_info(self) -> Dict[str, str]:
        """Get git info from the main project repo (parent of .aidocs)."""
        project_dir = self.aidocs_dir.parent
        try:
            hash_result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=project_dir,
                capture_output=True
            )
            branch_result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=project_dir,
                capture_output=True
            )
            if hash_result.returncode == 0:
                return {
                    'hash': hash_result.stdout.decode().strip(),
                    'branch': branch_result.stdout.decode().strip() if branch_result.returncode == 0 else 'unknown'
                }
        except Exception:
            pass
        return {}

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

    def _name_to_path(self, name: str) -> Path:
        """Convert doc name to file path. e.g., 'arch.overview' -> docs/arch/overview.md"""
        parts = name.split('.')
        return self.docs_dir / '/'.join(parts[:-1]) / f"{parts[-1]}.md" if len(parts) > 1 else self.docs_dir / f"{name}.md"

    def _read_file_content(self, file_path: Path) -> str:
        """Read content from a doc file."""
        if file_path.exists():
            return file_path.read_text()
        return ""

    def _write_file_content(self, file_path: Path, content: str) -> None:
        """Write content to a doc file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def doc_exists(self, name: str) -> bool:
        """Check if a document exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM docs WHERE name = ?", (name,))
            return cursor.fetchone() is not None

    def create_doc(self, name: str, description: str, content: str) -> Tuple[Doc, Optional[str]]:
        """Create a new document. Returns (doc, git_hash)."""
        now = datetime.now()
        file_path = self._name_to_path(name)

        # Write the file
        self._write_file_content(file_path, content)

        # Git commit the new file
        main_repo = self._get_main_repo_info()
        commit_msg = f"Create {name}: {description}"
        if main_repo:
            commit_msg += f"\n\nProject: {main_repo.get('hash', '')}@{main_repo.get('branch', '')}"
        git_hash = self._git_commit(file_path, commit_msg)

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
            cursor.execute("""
                INSERT INTO docs (name, description, file_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                doc.name,
                doc.description,
                str(file_path),
                doc.created_at.isoformat(),
                doc.updated_at.isoformat(),
            ))

        return doc, git_hash

    def get_doc(self, name: str) -> Optional[Doc]:
        """Get a document by name (reads content from file)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, description, file_path, created_at, updated_at
                FROM docs WHERE name = ?
            """, (name,))

            row = cursor.fetchone()
            if not row:
                return None

            file_path = Path(row['file_path'])
            content = self._read_file_content(file_path)

            # Get version count from git
            logs = self._git_log(file_path, limit=100)
            version = len(logs) if logs else 1

            return Doc(
                name=row['name'],
                version=version,
                description=row['description'],
                content=content,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
            )

    def get_doc_file_path(self, name: str) -> Optional[Path]:
        """Get the file path for a document."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM docs WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return Path(row['file_path'])
            return None

    def commit_doc(self, name: str, message: str, description: Optional[str] = None) -> Tuple[Doc, Optional[str]]:
        """Commit current file state as a new version. Returns (doc, git_hash)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, description, file_path, created_at, updated_at
                FROM docs WHERE name = ?
            """, (name,))

            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Document '{name}' not found")

            file_path = Path(row['file_path'])
            content = self._read_file_content(file_path)
            now = datetime.now()
            new_description = description if description else row['description']

            # Git commit with message + main repo context
            main_repo = self._get_main_repo_info()
            commit_msg = f"{name}: {message}"
            if main_repo:
                commit_msg += f"\n\nProject: {main_repo.get('hash', '')}@{main_repo.get('branch', '')}"
            git_hash = self._git_commit(file_path, commit_msg)

            # Get new version count from git
            logs = self._git_log(file_path, limit=100)
            new_version = len(logs) if logs else 1

            doc = Doc(
                name=name,
                version=new_version,
                description=new_description,
                content=content,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=now,
            )

            # Update metadata in SQLite
            cursor.execute("""
                UPDATE docs
                SET description = ?, updated_at = ?
                WHERE name = ?
            """, (
                doc.description,
                doc.updated_at.isoformat(),
                doc.name,
            ))

        return doc, git_hash

    def update_doc(self, name: str, description: str, content: str, message: str = "Updated") -> Tuple[Doc, Optional[str]]:
        """Update an existing document (writes file and commits)."""
        existing = self.get_doc(name)
        if not existing:
            raise ValueError(f"Document '{name}' not found")

        file_path = self._name_to_path(name)
        self._write_file_content(file_path, content)

        return self.commit_doc(name, message, description)

    def list_docs(self) -> List[Doc]:
        """Get all documents (metadata only, no content for efficiency)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, description, file_path, created_at, updated_at
                FROM docs
                ORDER BY name
            """)

            docs = []
            for row in cursor.fetchall():
                docs.append(Doc(
                    name=row['name'],
                    version=0,  # Version comes from git, not loaded here for efficiency
                    description=row['description'],
                    content="",
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                ))

            return docs

    def search_docs(self, query: str, limit: int = 10) -> List[Doc]:
        """Search documents by name and description only (not content)."""
        terms = query.lower().split()

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Build dynamic query for multiple search terms
            where_conditions = []
            where_params = []
            score_parts = []
            score_params = []

            for term in terms:
                # WHERE clause: only search name and description
                where_conditions.append("""
                    (LOWER(name) LIKE ? OR LOWER(description) LIKE ?)
                """)
                where_params.extend([f"%{term}%", f"%{term}%"])

                # Score: name matches worth more than description
                score_parts.append(f"""
                    (CASE WHEN LOWER(name) LIKE ? THEN 10 ELSE 0 END) +
                    (CASE WHEN LOWER(description) LIKE ? THEN 5 ELSE 0 END)
                """)
                score_params.extend([f"%{term}%", f"%{term}%"])

            where_clause = " AND ".join(where_conditions)
            score_clause = " + ".join(score_parts)

            params = score_params + where_params + [limit]

            query_sql = f"""
                SELECT name, description, file_path, created_at, updated_at,
                       ({score_clause}) as relevance_score
                FROM docs
                WHERE {where_clause}
                ORDER BY relevance_score DESC, name
                LIMIT ?
            """

            cursor.execute(query_sql, params)

            docs = []
            for row in cursor.fetchall():
                docs.append(Doc(
                    name=row['name'],
                    version=0,  # Version comes from git
                    description=row['description'],
                    content="",
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                ))

            return docs

    def get_doc_history(self, name: str) -> List[Dict[str, Any]]:
        """Get version history for a document from git."""
        file_path = self.get_doc_file_path(name)
        if not file_path:
            return []

        return self._git_log(file_path, limit=20)

    def delete_doc(self, name: str) -> bool:
        """Delete a document."""
        if not self.doc_exists(name):
            return False

        file_path = self.get_doc_file_path(name)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM docs WHERE name = ?", (name,))

        # Delete the file
        if file_path and file_path.exists():
            file_path.unlink()
            # Clean up empty parent directories
            try:
                file_path.parent.rmdir()
            except OSError:
                pass  # Directory not empty, that's fine

        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM docs")
            total_docs = cursor.fetchone()[0]

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

            # Count total commits across all docs from git
            total_commits = 0
            cursor.execute("SELECT file_path FROM docs")
            for row in cursor.fetchall():
                file_path = Path(row['file_path'])
                logs = self._git_log(file_path, limit=100)
                total_commits += len(logs)

            return {
                'total_docs': total_docs,
                'total_commits': total_commits,
                'recent_docs': recent_docs,
            }
