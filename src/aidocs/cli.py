"""
Main CLI interface for aidocs.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .database import Database
from .models import Doc
from .utils import (
    ensure_aidocs_dir,
    open_editor,
    generate_doc_template,
    format_search_results,
    build_hierarchy_tree,
    format_tree_display,
)


console = Console()


def get_database() -> Database:
    """Get database instance for the current project."""
    aidocs_dir = ensure_aidocs_dir()
    return Database(aidocs_dir / 'store.db')


@click.group()
@click.version_option()
def cli():
    """aidocs - AI-Native Architecture Documentation System"""
    pass


@cli.command()
def init():
    """Initialize .aidocs/ in current directory."""
    aidocs_dir = ensure_aidocs_dir()

    if (aidocs_dir / 'store.db').exists():
        console.print(f"[yellow]aidocs already initialized in {aidocs_dir}[/yellow]")
        return

    # Initialize database
    db = get_database()

    # Create gitignore entry suggestion
    gitignore_path = Path.cwd() / '.gitignore'
    gitignore_content = "\n# aidocs (local documentation)\n.aidocs/\n"

    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            current_content = f.read()
        if '.aidocs/' not in current_content:
            console.print(f"[yellow]Consider adding to {gitignore_path}:[/yellow]")
            console.print(gitignore_content)
    else:
        console.print(f"[yellow]Consider creating {gitignore_path} with:[/yellow]")
        console.print(gitignore_content)

    console.print(f"[green]✓ Initialized aidocs in {aidocs_dir}[/green]")
    console.print("\nNext steps:")
    console.print("  1. aidocs store <concept> \"<description>\" \"<content>\"")
    console.print("  2. aidocs search \"<keywords>\"")
    console.print("  3. aidocs list")


@cli.command()
@click.argument('name')
@click.argument('description')
@click.argument('content')
@click.option('--update', is_flag=True, help='Update existing doc instead of creating new')
def store(name: str, description: str, content: str, update: bool):
    """Store documentation created by AI (primary creation command)."""
    if not Doc.is_valid_name(name):
        console.print(f"[red]Error: Invalid name '{name}'[/red]")
        console.print("Use lowercase with dots for hierarchy: 'auth.jwt.middleware'")
        sys.exit(1)

    db = get_database()

    try:
        if update:
            if not db.doc_exists(name):
                console.print(f"[red]Error: Doc '{name}' doesn't exist. Remove --update flag to create.[/red]")
                sys.exit(1)
            doc = db.update_doc(name, description, content)
            console.print(f"[green]✓ Updated doc: {name} (v{doc.version})[/green]")
        else:
            if db.doc_exists(name):
                console.print(f"[red]Error: Doc '{name}' already exists. Use --update flag to modify.[/red]")
                sys.exit(1)
            doc = db.create_doc(name, description, content)
            console.print(f"[green]✓ Created doc: {name}[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('name')
@click.option('--edit', is_flag=True, help='Open in editor for modification')
def add(name: str, edit: bool):
    """Create or update documentation (interactive editor)."""
    if not Doc.is_valid_name(name):
        console.print(f"[red]Error: Invalid name '{name}'[/red]")
        console.print("Use lowercase with dots for hierarchy: 'auth.jwt.middleware'")
        sys.exit(1)

    db = get_database()
    existing_doc = db.get_doc(name)

    if existing_doc and not edit:
        console.print(f"[yellow]Doc '{name}' already exists.[/yellow]")
        console.print("Use 'aidocs add --edit' to modify or 'aidocs show' to view.")
        sys.exit(1)

    # Prepare content for editor
    if existing_doc:
        initial_content = f"# {existing_doc.name}\n\n## Description\n{existing_doc.description}\n\n{existing_doc.content}"
    else:
        initial_content = generate_doc_template(name)

    # Open editor
    edited_content = open_editor(initial_content)
    if edited_content is None:
        console.print("[yellow]Edit cancelled.[/yellow]")
        return

    # Parse the edited content to extract description
    lines = edited_content.split('\n')
    description = ""
    content_lines = []
    in_description = False

    for line in lines:
        if line.strip() == "## Description":
            in_description = True
            continue
        elif line.startswith("## ") and in_description:
            in_description = False

        if in_description and line.strip():
            description = line.strip()
        elif not in_description:
            content_lines.append(line)

    content = '\n'.join(content_lines).strip()

    if not description:
        console.print("[red]Error: Description is required[/red]")
        sys.exit(1)

    try:
        if existing_doc:
            doc = db.update_doc(name, description, content)
            console.print(f"[green]✓ Updated doc: {name} (v{doc.version})[/green]")
        else:
            doc = db.create_doc(name, description, content)
            console.print(f"[green]✓ Created doc: {name}[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--limit', default=10, help='Maximum number of results')
@click.option('--show-content', is_flag=True, help='Include content preview in results')
def search(query: str, limit: int, show_content: bool):
    """Search documentation by keywords."""
    db = get_database()
    docs = db.search_docs(query, limit)

    if not docs:
        console.print(f"[yellow]No docs found for '{query}'[/yellow]")
        console.print("\nTo create documentation:")
        console.print(f'  aidocs store "{query}" "<description>" "<content>"')
        return

    console.print(f"[bold]Found {len(docs)} result(s) for '{query}':[/bold]\n")

    for i, doc in enumerate(docs, 1):
        console.print(f"[bold blue]{i}. {doc.name}[/bold blue]")
        console.print(f"   {doc.description}")

        if show_content:
            # Show first 200 characters of content
            content_preview = doc.content.replace('\n', ' ')
            if len(content_preview) > 200:
                content_preview = content_preview[:197] + "..."
            console.print(f"   [dim]{content_preview}[/dim]")

        console.print()

    console.print(f"[dim]Use 'aidocs show <name>' to read full documentation.[/dim]")


@cli.command()
@click.argument('name')
def show(name: str):
    """Show documentation for a concept."""
    db = get_database()
    doc = db.get_doc(name)

    if not doc:
        console.print(f"[red]No doc found: {name}[/red]")

        # Suggest similar documents
        search_results = db.search_docs(name, 3)
        if search_results:
            console.print(f"\n[yellow]Similar docs:[/yellow]")
            for result in search_results:
                console.print(f"  • {result.name} - {result.description}")
        return

    # Create rich display
    panel_content = []

    # Header with metadata
    header = f"[bold]{doc.name}[/bold] (v{doc.version})"
    if doc.created_at != doc.updated_at:
        header += f" • Updated {doc.updated_at.strftime('%Y-%m-%d %H:%M')}"
    else:
        header += f" • Created {doc.created_at.strftime('%Y-%m-%d %H:%M')}"

    console.print(Panel(header, style="blue"))

    # Description
    console.print(f"\n[italic]{doc.description}[/italic]\n")

    # Content
    console.print(doc.content)


@cli.command()
@click.option('--tree', is_flag=True, help='Display in hierarchical tree format')
def list(tree: bool):
    """List all documented concepts."""
    db = get_database()
    docs = db.list_docs()

    if not docs:
        console.print("[yellow]No documents found.[/yellow]")
        console.print("\nCreate your first doc:")
        console.print('  aidocs store "auth" "Authentication system" "Description of auth..."')
        return

    if tree:
        console.print(f"[bold]Documented Concepts ({len(docs)} total):[/bold]\n")
        hierarchy = build_hierarchy_tree(docs)
        tree_display = format_tree_display(hierarchy)
        console.print(tree_display)
    else:
        console.print(f"[bold]Documented Concepts ({len(docs)} total):[/bold]\n")

        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description")
        table.add_column("Updated", style="dim", no_wrap=True)

        for doc in docs:
            table.add_row(
                doc.name,
                doc.description,
                doc.updated_at.strftime('%Y-%m-%d')
            )

        console.print(table)

    console.print(f"\n[dim]Use 'aidocs search <query>' to find specific topics[/dim]")
    console.print(f"[dim]Use 'aidocs show <concept>' to read full documentation[/dim]")


@cli.command()
@click.argument('name')
@click.argument('content')
@click.option('--section', default='Current Work', help='Section to append to')
def append(name: str, content: str, section: str):
    """Append information to existing doc section."""
    db = get_database()
    doc = db.get_doc(name)

    if not doc:
        console.print(f"[red]Error: Doc '{name}' not found[/red]")
        sys.exit(1)

    # Find the section and append content
    lines = doc.content.split('\n')
    section_header = f"## {section}"
    section_found = False
    new_lines = []

    for line in lines:
        new_lines.append(line)
        if line.strip() == section_header:
            section_found = True
            new_lines.append(f"- {content}")

    if not section_found:
        # Add new section at the end
        new_lines.append("")
        new_lines.append(section_header)
        new_lines.append(f"- {content}")

    new_content = '\n'.join(new_lines)

    try:
        updated_doc = db.update_doc(name, doc.description, new_content)
        console.print(f"[green]✓ Added to {section} in {name} (v{updated_doc.version})[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command(name='record-decision')
@click.argument('name')
@click.argument('decision')
@click.argument('rationale')
def record_decision(name: str, decision: str, rationale: str):
    """Record a decision made while working on concept."""
    db = get_database()
    doc = db.get_doc(name)

    if not doc:
        console.print(f"[red]Error: Doc '{name}' not found[/red]")
        sys.exit(1)

    # Add decision to the doc content
    date_str = datetime.now().strftime('%Y-%m-%d')
    decision_text = f"""
**Decision**: {decision}
**Chosen**: [Record your choice]
**Rationale**: {rationale}
**Date**: {date_str}
"""

    # Find Decisions section or create it
    lines = doc.content.split('\n')
    decisions_found = False
    new_lines = []

    for line in lines:
        new_lines.append(line)
        if line.strip() == "## Decisions Made":
            decisions_found = True
            new_lines.append(decision_text)

    if not decisions_found:
        # Add new section at the end
        new_lines.append("")
        new_lines.append("## Decisions Made")
        new_lines.append(decision_text)

    new_content = '\n'.join(new_lines)

    try:
        updated_doc = db.update_doc(name, doc.description, new_content)
        console.print(f"[green]✓ Recorded decision in {name} (v{updated_doc.version})[/green]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument('name')
def log(name: str):
    """Show version history for a concept."""
    db = get_database()
    doc = db.get_doc(name)

    if not doc:
        console.print(f"[red]Doc '{name}' not found[/red]")
        return

    history = db.get_doc_history(name)

    console.print(f"[bold]Version history for {name}:[/bold]\n")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Version", style="cyan")
    table.add_column("Description")
    table.add_column("Date", style="dim")

    for entry in history:
        table.add_row(
            str(entry['version']),
            entry['description'],
            entry['created_at']
        )

    console.print(table)


@cli.command()
@click.argument('query')
def why(query: str):
    """Search architectural decisions and rationale."""
    db = get_database()

    # Search in content for decision-related keywords
    decision_query = f"{query} decision rationale"
    docs = db.search_docs(decision_query, 5)

    if not docs:
        console.print(f"[yellow]No decisions found for '{query}'[/yellow]")
        return

    console.print(f"[bold]Decisions related to '{query}':[/bold]\n")

    for doc in docs:
        # Extract decision sections from content
        lines = doc.content.split('\n')
        in_decisions = False
        decision_lines = []

        for line in lines:
            if '## Decisions' in line:
                in_decisions = True
                continue
            elif line.startswith('## ') and in_decisions:
                break
            elif in_decisions and line.strip():
                decision_lines.append(line)

        if decision_lines:
            console.print(f"[bold blue]{doc.name}[/bold blue]")
            console.print('\n'.join(decision_lines[:5]))  # Show first 5 lines
            console.print()


@cli.command()
def status():
    """Show overview of documented concepts and recent updates."""
    db = get_database()
    stats = db.get_stats()

    console.print("[bold]aidocs Status[/bold]\n")

    # Summary stats
    console.print(f"📚 Total documents: {stats['total_docs']}")
    console.print(f"📝 Total versions: {stats['total_versions']}")
    console.print()

    # Recent activity
    if stats['recent_docs']:
        console.print("[bold]Recent updates:[/bold]")
        for recent in stats['recent_docs']:
            console.print(f"  • {recent['name']} - {recent['updated_at']}")
        console.print()

    console.print("[dim]Use 'aidocs list' to see all documents[/dim]")
    console.print("[dim]Use 'aidocs search <query>' to find specific topics[/dim]")


if __name__ == '__main__':
    cli()