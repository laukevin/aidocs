"""
Shell completion support for aidocs.
"""

import click
from pathlib import Path
from .database import Database
from .utils import get_aidocs_dir


def complete_concept_names(ctx, param, incomplete):
    """Complete concept names from existing documentation."""
    try:
        aidocs_dir = get_aidocs_dir()
        if not (aidocs_dir / 'store.db').exists():
            return []

        db = Database(aidocs_dir / 'store.db')
        docs = db.list_docs()

        # Filter by incomplete text
        matches = [doc.name for doc in docs if doc.name.startswith(incomplete)]
        return matches[:10]  # Limit to 10 completions
    except Exception:
        return []


def complete_search_terms(ctx, param, incomplete):
    """Complete search terms based on existing doc content."""
    try:
        aidocs_dir = get_aidocs_dir()
        if not (aidocs_dir / 'store.db').exists():
            return []

        db = Database(aidocs_dir / 'store.db')
        docs = db.list_docs()

        # Extract common terms from descriptions
        terms = set()
        for doc in docs:
            words = doc.description.lower().split()
            terms.update(word.strip('.,!?') for word in words if len(word) > 2)

        # Filter by incomplete text
        matches = [term for term in terms if term.startswith(incomplete.lower())]
        return sorted(matches)[:10]
    except Exception:
        return []


def complete_sections(ctx, param, incomplete):
    """Complete common section names for append command."""
    sections = [
        "Current Work",
        "Recent Changes",
        "Decisions Made",
        "Notes",
        "Architecture",
        "Testing",
        "Tools & Commands",
        "Key Files"
    ]

    matches = [section for section in sections if section.lower().startswith(incomplete.lower())]
    return matches


# Register completions with click commands
concept_name_completion = click.Choice([])  # Will be populated dynamically
concept_name_completion.complete = complete_concept_names

search_term_completion = click.Choice([])  # Will be populated dynamically
search_term_completion.complete = complete_search_terms

section_name_completion = click.Choice([])  # Will be populated dynamically
section_name_completion.complete = complete_sections