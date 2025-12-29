#!/usr/bin/env python3

import sys
import os
import subprocess
from pathlib import Path
sys.path.insert(0, '/data/projects/aidocs/src')

def run_aidocs_command(cmd_args):
    """Run aidocs command and capture output."""
    env = os.environ.copy()
    env['PYTHONPATH'] = '/data/projects/aidocs/src'

    result = subprocess.run(
        ['python3', '-m', 'aidocs.cli'] + cmd_args,
        cwd='/data/projects/aidocs/examples/test_project',
        capture_output=True,
        text=True,
        env=env
    )

    print(f"Command: aidocs {' '.join(cmd_args)}")
    print(f"Return code: {result.returncode}")
    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")
    print("=" * 50)
    return result

def check_database_direct():
    """Check database contents directly."""
    try:
        from aidocs.database import Database
        db = Database(Path('.aidocs/store.db'))
        docs = db.list_docs()
        print(f"Direct database check: Found {len(docs)} docs")
        for doc in docs:
            print(f"  - {doc.name}: {doc.description}")
    except Exception as e:
        print(f"Database check failed: {e}")
    print("=" * 50)

def main():
    # Clean start
    if os.path.exists('.aidocs'):
        import shutil
        shutil.rmtree('.aidocs')

    print("=== Detailed CLI Testing ===\n")

    # Test 1: Init
    print("1. Testing init...")
    run_aidocs_command(['init'])
    check_database_direct()

    # Test 2: Store first doc
    print("2. Testing store auth.manager...")
    result = run_aidocs_command([
        'store',
        'auth.manager',
        'Authentication management system',
        'The AuthManager class handles user authentication and registration.'
    ])
    check_database_direct()

    # Test 3: List docs
    print("3. Testing list...")
    run_aidocs_command(['list'])

    # Test 4: Show doc
    print("4. Testing show...")
    run_aidocs_command(['show', 'auth.manager'])

    # Test 5: Search
    print("5. Testing search...")
    run_aidocs_command(['search', 'authentication'])
    run_aidocs_command(['search', 'manager'])
    run_aidocs_command(['search', 'AuthManager'])

if __name__ == '__main__':
    main()