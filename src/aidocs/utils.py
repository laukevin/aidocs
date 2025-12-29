"""
Utility functions for aidocs.
"""

import os
import tempfile
import subprocess
from pathlib import Path
from typing import Optional


def get_aidocs_dir() -> Path:
    """Get the .aidocs directory in the current project."""
    current = Path.cwd()

    # Look for .aidocs in current directory or parent directories
    while current != current.parent:
        aidocs_dir = current / '.aidocs'
        if aidocs_dir.exists():
            return aidocs_dir
        current = current.parent

    # Default to current directory if not found
    return Path.cwd() / '.aidocs'


def ensure_aidocs_dir() -> Path:
    """Ensure .aidocs directory exists and return its path."""
    aidocs_dir = get_aidocs_dir()
    aidocs_dir.mkdir(exist_ok=True)
    return aidocs_dir


def open_editor(content: str = "", file_extension: str = ".md") -> Optional[str]:
    """
    Open content in user's preferred editor and return the edited content.
    Returns None if user cancels/doesn't save.
    """
    editor = os.environ.get('EDITOR', 'nano')

    with tempfile.NamedTemporaryFile(
        mode='w+',
        suffix=file_extension,
        delete=False
    ) as temp_file:
        temp_file.write(content)
        temp_file.flush()
        temp_file_path = temp_file.name

    try:
        # Open editor
        result = subprocess.run([editor, temp_file_path], check=True)

        # Read the edited content
        with open(temp_file_path, 'r') as f:
            edited_content = f.read()

        return edited_content.strip()

    except subprocess.CalledProcessError:
        # User cancelled or editor failed
        return None
    except KeyboardInterrupt:
        # User cancelled with Ctrl+C
        return None
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_file_path)
        except OSError:
            pass


def generate_doc_template(name: str) -> str:
    """Generate a markdown template for a new document."""
    return f"""# {name}

## Description
[Brief one-line description for search results]

## Current State
[How this works right now]

## Architecture
[Key components, patterns, dependencies]

## Key Files
[Important files and their roles]

## Testing
[How to verify this works]

## Tools & Commands
[Relevant commands, scripts, deployment info]

## Recent Changes
[What changed recently and when]

## Decisions Made
[Key decisions with rationale and dates]

## Notes
[Additional context, gotchas, future considerations]
"""


def format_doc_list_item(name: str, description: str, max_desc_length: int = 60) -> str:
    """Format a document for list display."""
    if len(description) > max_desc_length:
        description = description[:max_desc_length - 3] + "..."

    # Calculate padding for alignment
    max_name_length = 25
    if len(name) > max_name_length:
        name_part = name[:max_name_length - 3] + "..."
    else:
        name_part = name.ljust(max_name_length)

    return f"{name_part} {description}"


def format_search_results(docs, query: str, show_content: bool = False) -> str:
    """Format search results for display."""
    if not docs:
        return f"No docs found for '{query}'.\n\nUse 'aidocs store \"{query}\" \"<description>\" \"<content>\"' to create documentation."

    result = f"Found {len(docs)} result(s) for '{query}':\n\n"

    for i, doc in enumerate(docs, 1):
        result += f"{i}. {doc.name}\n"
        result += f"   {doc.description}\n"

        if show_content:
            # Show first 200 characters of content
            content_preview = doc.content.replace('\n', ' ')
            if len(content_preview) > 200:
                content_preview = content_preview[:197] + "..."
            result += f"   {content_preview}\n"

        result += "\n"

    result += "Use 'aidocs show <name>' to read full documentation."
    return result


def build_hierarchy_tree(docs) -> dict:
    """Build a hierarchical tree structure from doc names."""
    tree = {}

    for doc in docs:
        parts = doc.name.split('.')
        current = tree

        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # Leaf node
                current[part] = doc
            else:
                # Branch node
                if part not in current:
                    current[part] = {}
                current = current[part]

    return tree


def format_tree_display(tree, indent: int = 0, prefix: str = "") -> str:
    """Format hierarchical tree for display."""
    result = ""
    items = sorted(tree.items())

    for i, (name, value) in enumerate(items):
        is_last = i == len(items) - 1
        current_prefix = "└── " if is_last else "├── "
        next_prefix = "    " if is_last else "│   "

        if hasattr(value, 'description'):  # It's a Doc object
            result += f"{prefix}{current_prefix}{name} - {value.description}\n"
        else:  # It's a nested dict
            result += f"{prefix}{current_prefix}{name}/\n"
            result += format_tree_display(
                value,
                indent + 1,
                prefix + next_prefix
            )

    return result