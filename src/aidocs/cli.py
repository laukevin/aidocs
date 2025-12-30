"""
Main CLI interface for aidocs.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Note: Shell completion helpers available in completion.py for future use
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


def add_to_gitignore() -> bool:
    """Add .aidocs/ to .gitignore if not already present. Returns True if modified."""
    gitignore_path = Path.cwd() / '.gitignore'
    gitignore_entry = ".aidocs/"

    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            content = f.read()
        if gitignore_entry in content:
            return False
        with open(gitignore_path, 'a') as f:
            f.write(f"\n# aidocs (local AI documentation)\n{gitignore_entry}\n")
    else:
        with open(gitignore_path, 'w') as f:
            f.write(f"# aidocs (local AI documentation)\n{gitignore_entry}\n")
    return True


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
def setup():
    """Full stealth setup: init + gitignore + hooks (run this in your project)."""
    console.print("[bold]aidocs Setup[/bold]\n")

    # Step 1: Initialize .aidocs/
    aidocs_dir = Path.cwd() / '.aidocs'
    if aidocs_dir.exists() and (aidocs_dir / 'store.db').exists():
        console.print("[dim]1.[/dim] [yellow]Already initialized[/yellow]")
    else:
        ensure_aidocs_dir()
        get_database()  # Creates the database
        console.print("[dim]1.[/dim] [green]✓ Created .aidocs/[/green]")

    # Step 2: Add to .gitignore (stealth mode)
    if add_to_gitignore():
        console.print("[dim]2.[/dim] [green]✓ Added .aidocs/ to .gitignore[/green]")
    else:
        console.print("[dim]2.[/dim] [yellow]Already in .gitignore[/yellow]")

    # Step 3: Check/install hooks
    settings_path = get_claude_settings_path()
    local_settings_path = get_claude_local_settings_path()
    settings = load_claude_settings(settings_path)
    local_settings = load_claude_settings(local_settings_path)

    hooks_ok = True
    for hook_type in ['SessionStart', 'PreCompact']:
        if not (has_aidocs_hook(settings, hook_type) or has_aidocs_hook(local_settings, hook_type)):
            hooks_ok = False
            break

    if hooks_ok:
        console.print("[dim]3.[/dim] [yellow]Hooks already configured[/yellow]")
    else:
        # Install hooks
        for hook_type in ['SessionStart', 'PreCompact']:
            if not has_aidocs_hook(settings, hook_type):
                settings = add_aidocs_hook(settings, hook_type)
        save_claude_settings(settings_path, settings)
        console.print("[dim]3.[/dim] [green]✓ Installed Claude Code hooks[/green]")

    # Done
    console.print("\n[green]Setup complete![/green]")
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Restart Claude Code (or start a new session)")
    console.print("  2. Claude will automatically see aidocs context")
    console.print("  3. Claude will read/write docs as it works")
    console.print("\n[dim]The AI uses aidocs - you don't need to run commands manually.[/dim]")


@cli.command()
@click.argument('name')
@click.argument('description')
@click.argument('content')
def store(name: str, description: str, content: str):
    """Create a new document (for existing docs, use show + Edit + commit)."""
    if not Doc.is_valid_name(name):
        console.print(f"[red]Error: Invalid name '{name}'[/red]")
        console.print("Use lowercase with dots for hierarchy: 'auth.jwt.middleware'")
        sys.exit(1)

    db = get_database()

    if db.doc_exists(name):
        console.print(f"[red]Error: Doc '{name}' already exists.[/red]")
        console.print(f"[dim]To update: aidocs show {name} → Edit file → aidocs commit {name} \"message\"[/dim]")
        sys.exit(1)

    try:
        doc, git_hash = db.create_doc(name, description, content)
        hash_str = f" [{git_hash}]" if git_hash else ""
        console.print(f"[green]✓ Created doc: {name}{hash_str}[/green]")
        console.print(f"[dim]File: {db.get_doc_file_path(name)}[/dim]")
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
def search(query: str, limit: int):
    """Search documentation by name and description."""
    db = get_database()
    docs = db.search_docs(query, limit)

    if not docs:
        console.print(f"[yellow]No docs found for '{query}'[/yellow]")
        console.print("\nTo create documentation:")
        console.print(f'  aidocs store "{query}" "<description>" "<content>"')
        return

    console.print(f"[bold]Found {len(docs)} result(s) for '{query}':[/bold]\n")

    for i, doc in enumerate(docs, 1):
        file_path = db.get_doc_file_path(doc.name)
        console.print(f"[bold blue]{i}. {doc.name}[/bold blue] (v{doc.version})")
        console.print(f"   {doc.description}")
        console.print(f"   [dim]{file_path}[/dim]")
        console.print()

    console.print(f"[dim]Use 'aidocs show <name>' to get file path for reading/editing.[/dim]")


@cli.command()
@click.argument('name')
def show(name: str):
    """Show file path for a document (use Read tool to view content)."""
    db = get_database()
    file_path = db.get_doc_file_path(name)

    if not file_path:
        console.print(f"[red]No doc found: {name}[/red]")

        # Suggest similar documents
        search_results = db.search_docs(name, 3)
        if search_results:
            console.print(f"\n[yellow]Similar docs:[/yellow]")
            for result in search_results:
                console.print(f"  • {result.name} - {result.description}")
        return

    doc = db.get_doc(name)

    # Output the file path (this is what the AI needs)
    console.print(f"[bold]File:[/bold] {file_path.absolute()}")
    console.print(f"[dim]Version: {doc.version} | {doc.description}[/dim]")
    console.print(f"\n[dim]Use Read tool to view content, Edit tool to modify, then 'aidocs commit {name}' to save.[/dim]")


@cli.command()
@click.argument('name')
@click.argument('message')
@click.option('--description', '-d', default=None, help='Update doc description')
def commit(name: str, message: str, description: Optional[str]):
    """Commit current file changes as a new version with a message.

    MESSAGE describes what changed in this version (required).
    """
    db = get_database()

    if not db.doc_exists(name):
        console.print(f"[red]Error: Doc '{name}' not found[/red]")
        sys.exit(1)

    try:
        doc, git_hash = db.commit_doc(name, message, description)
        hash_str = f" [{git_hash}]" if git_hash else ""
        console.print(f"[green]✓ Committed {name} v{doc.version}{hash_str}[/green]")
        console.print(f"[dim]Message: {message}[/dim]")
    except ValueError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


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
    """Show version history for a document (from git)."""
    db = get_database()
    doc = db.get_doc(name)

    if not doc:
        console.print(f"[red]Doc '{name}' not found[/red]")
        return

    history = db.get_doc_history(name)

    if not history:
        console.print(f"[yellow]No version history found for {name}[/yellow]")
        return

    console.print(f"[bold]Version history for {name}:[/bold]\n")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Hash", style="cyan")
    table.add_column("Message")
    table.add_column("Date", style="dim")

    for entry in history:
        table.add_row(
            entry['hash'],
            entry['message'],
            entry['date']
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
    console.print(f"📝 Total commits: {stats['total_commits']}")
    console.print()

    # Recent activity
    if stats['recent_docs']:
        console.print("[bold]Recent updates:[/bold]")
        for recent in stats['recent_docs']:
            console.print(f"  • {recent['name']} - {recent['updated_at']}")
        console.print()

    console.print("[dim]Use 'aidocs list' to see all documents[/dim]")
    console.print("[dim]Use 'aidocs search <query>' to find specific topics[/dim]")


@cli.command()
def prime():
    """Output context for AI assistants (used by Claude Code hooks)."""
    aidocs_dir = Path.cwd() / '.aidocs'

    # Check if aidocs is initialized
    if not aidocs_dir.exists() or not (aidocs_dir / 'store.db').exists():
        # Silent exit if not initialized - don't spam non-aidocs projects
        return

    db = get_database()
    stats = db.get_stats()
    docs = db.list_docs()

    # Build the context output (plain text for hook consumption)
    output = []
    output.append("# aidocs - Architecture Documentation Context")
    output.append("")
    output.append("> **Context Recovery**: Run `aidocs prime` after compaction or new session")
    output.append("")

    # Current status
    output.append(f"## Documentation Status: {stats['total_docs']} docs, {stats['total_commits']} commits")
    output.append("")

    # List documented concepts if any exist
    if docs:
        output.append("### Documented Concepts")
        for doc in docs[:15]:  # Limit to avoid overwhelming context
            output.append(f"- **{doc.name}**: {doc.description}")
        if len(docs) > 15:
            output.append(f"- ... and {len(docs) - 15} more (use `aidocs list` to see all)")
        output.append("")

    # Recent updates
    if stats['recent_docs']:
        output.append("### Recent Updates")
        for recent in stats['recent_docs'][:5]:
            output.append(f"- {recent['name']} ({recent['updated_at']})")
        output.append("")

    # Instructions for AI
    output.append("## AI Documentation Workflow")
    output.append("")
    output.append("### Step 1: Search for existing docs")
    output.append("Before planning or research, always check what's documented:")
    output.append("```")
    output.append("aidocs search \"<topic>\"    # Search by name/description, returns top 10")
    output.append("aidocs list                 # See all documented concepts")
    output.append("```")
    output.append("")
    output.append("### Step 2: Read a doc (get file path)")
    output.append("```")
    output.append("aidocs show <name>          # Returns file path to the doc")
    output.append("```")
    output.append("Then use your Read tool on that file path to view content.")
    output.append("")
    output.append("### Step 3: Create NEW doc")
    output.append("If no relevant doc exists:")
    output.append("```")
    output.append("aidocs store <name> \"<description>\" \"<initial content>\"")
    output.append("```")
    output.append("Names use dot-hierarchy: `arch.overview`, `api.auth`, `plan.feature-x`")
    output.append("")
    output.append("### Step 4: Edit EXISTING doc")
    output.append("```")
    output.append("aidocs show <name>                    # 1. Get file path")
    output.append("# Use Read tool to view               # 2. Read current content")
    output.append("# Use Edit tool to modify             # 3. Make targeted changes")
    output.append("aidocs commit <name> \"<message>\"     # 4. Commit with description of changes")
    output.append("```")
    output.append("The commit message describes what changed. Git hash/date are recorded automatically.")
    output.append("")
    output.append("### When to WRITE docs (PLANNING/RESEARCH only)")
    output.append("- Exploring codebase → document structure/layout")
    output.append("- Investigating architecture → record patterns")
    output.append("- Creating plans → save before implementing")
    output.append("- Major decisions → record with rationale")
    output.append("")
    output.append("### When to READ docs (IMPLEMENTING)")
    output.append("- Check existing docs before coding")
    output.append("- Reference plan docs from planning phase")
    output.append("- Do NOT create new docs while implementing")
    output.append("")
    output.append("### What to document")
    output.append("- Major architecture patterns and decisions")
    output.append("- Codebase layout and structure")
    output.append("- Implementation plans before starting work")
    output.append("")
    output.append("### What NOT to document")
    output.append("- Small changes, constants, minor refactors")
    output.append("- Obvious implementation details")
    output.append("")
    output.append("### Other commands")
    output.append("- `aidocs log <name>` - View version history")
    output.append("- `aidocs why \"<topic>\"` - Search past decisions")
    output.append("")

    # Print as plain text (hooks capture stdout)
    print('\n'.join(output))


def get_claude_settings_path() -> Path:
    """Get the path to Claude Code settings file."""
    return Path.home() / '.claude' / 'settings.json'


def get_claude_local_settings_path() -> Path:
    """Get the path to Claude Code local settings file."""
    return Path.home() / '.claude' / 'settings.local.json'


def load_claude_settings(path: Path) -> dict:
    """Load Claude Code settings from a file."""
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def save_claude_settings(path: Path, settings: dict) -> None:
    """Save Claude Code settings to a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(settings, f, indent=2)


def has_aidocs_hook(settings: dict, hook_type: str) -> bool:
    """Check if aidocs hook exists in settings."""
    hooks = settings.get('hooks', {}).get(hook_type, [])
    for hook_group in hooks:
        for hook in hook_group.get('hooks', []):
            if hook.get('command') == 'aidocs prime':
                return True
    return False


def add_aidocs_hook(settings: dict, hook_type: str) -> dict:
    """Add aidocs hook to settings."""
    if 'hooks' not in settings:
        settings['hooks'] = {}
    if hook_type not in settings['hooks']:
        settings['hooks'][hook_type] = []

    # Add aidocs hook
    settings['hooks'][hook_type].append({
        'hooks': [{'command': 'aidocs prime', 'type': 'command'}],
        'matcher': ''
    })
    return settings


@cli.command('install-hooks')
@click.option('--local', is_flag=True, help='Install to settings.local.json instead of settings.json')
def install_hooks(local: bool):
    """Install aidocs hooks into Claude Code settings."""
    if local:
        settings_path = get_claude_local_settings_path()
    else:
        settings_path = get_claude_settings_path()

    settings = load_claude_settings(settings_path)

    modified = False
    for hook_type in ['SessionStart', 'PreCompact']:
        if not has_aidocs_hook(settings, hook_type):
            settings = add_aidocs_hook(settings, hook_type)
            console.print(f"[green]✓ Added aidocs hook to {hook_type}[/green]")
            modified = True
        else:
            console.print(f"[yellow]• {hook_type} hook already exists[/yellow]")

    if modified:
        save_claude_settings(settings_path, settings)
        console.print(f"\n[green]✓ Saved to {settings_path}[/green]")
        console.print("\n[dim]Restart Claude Code for hooks to take effect.[/dim]")
    else:
        console.print("\n[dim]No changes needed - hooks already installed.[/dim]")


@cli.command('uninstall-hooks')
@click.option('--local', is_flag=True, help='Uninstall from settings.local.json')
def uninstall_hooks(local: bool):
    """Remove aidocs hooks from Claude Code settings."""
    if local:
        settings_path = get_claude_local_settings_path()
    else:
        settings_path = get_claude_settings_path()

    if not settings_path.exists():
        console.print(f"[yellow]No settings file found at {settings_path}[/yellow]")
        return

    settings = load_claude_settings(settings_path)
    modified = False

    for hook_type in ['SessionStart', 'PreCompact']:
        if hook_type in settings.get('hooks', {}):
            original_len = len(settings['hooks'][hook_type])
            settings['hooks'][hook_type] = [
                hg for hg in settings['hooks'][hook_type]
                if not any(h.get('command') == 'aidocs prime' for h in hg.get('hooks', []))
            ]
            if len(settings['hooks'][hook_type]) < original_len:
                console.print(f"[green]✓ Removed aidocs hook from {hook_type}[/green]")
                modified = True

    if modified:
        save_claude_settings(settings_path, settings)
        console.print(f"\n[green]✓ Saved to {settings_path}[/green]")
    else:
        console.print("[dim]No aidocs hooks found to remove.[/dim]")


@cli.command()
def doctor():
    """Check aidocs installation and hook configuration."""
    console.print("[bold]aidocs Doctor[/bold]\n")

    all_ok = True

    # Check 1: aidocs command available
    console.print("[bold]1. Command availability[/bold]")
    console.print("   [green]✓ aidocs command is available[/green]")

    # Check 2: Claude Code settings
    console.print("\n[bold]2. Claude Code hooks[/bold]")

    settings_path = get_claude_settings_path()
    local_settings_path = get_claude_local_settings_path()

    # Check main settings
    settings = load_claude_settings(settings_path)
    local_settings = load_claude_settings(local_settings_path)

    for hook_type in ['SessionStart', 'PreCompact']:
        has_hook = has_aidocs_hook(settings, hook_type) or has_aidocs_hook(local_settings, hook_type)
        if has_hook:
            console.print(f"   [green]✓ {hook_type} hook configured[/green]")
        else:
            console.print(f"   [red]✗ {hook_type} hook missing[/red]")
            all_ok = False

    # Check 3: Current project initialization
    console.print("\n[bold]3. Current project[/bold]")
    aidocs_dir = Path.cwd() / '.aidocs'
    if aidocs_dir.exists() and (aidocs_dir / 'store.db').exists():
        db = get_database()
        stats = db.get_stats()
        console.print(f"   [green]✓ Initialized in {aidocs_dir}[/green]")
        console.print(f"   [dim]  {stats['total_docs']} docs, {stats['total_commits']} commits[/dim]")
    else:
        console.print(f"   [yellow]• Not initialized in current directory[/yellow]")
        console.print(f"   [dim]  Run 'aidocs init' to initialize[/dim]")

    # Summary
    console.print()
    if all_ok:
        console.print("[green]All checks passed![/green]")
    else:
        console.print("[yellow]Some issues found. Run 'aidocs install-hooks' to fix.[/yellow]")


if __name__ == '__main__':
    cli()