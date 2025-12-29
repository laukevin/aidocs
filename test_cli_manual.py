#!/usr/bin/env python3
"""
Manual CLI testing script.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from aidocs.cli import cli
from click.testing import CliRunner


def test_basic_workflow():
    """Test the basic aidocs workflow."""
    print("🧪 Testing aidocs CLI workflow...")

    # Create temp directory for testing
    temp_dir = tempfile.mkdtemp()
    original_cwd = os.getcwd()

    try:
        os.chdir(temp_dir)
        runner = CliRunner()

        # Test 1: Initialize
        print("\n1. Testing init command...")
        result = runner.invoke(cli, ['init'])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        assert Path('.aidocs').exists()
        print("   ✅ Init successful")

        # Test 2: Store a document
        print("\n2. Testing store command...")
        result = runner.invoke(cli, [
            'store',
            'auth.jwt',
            'JWT authentication system',
            'This system handles JWT token validation and generation for API authentication.'
        ])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        print("   ✅ Store successful")

        # Test 3: Show the document
        print("\n3. Testing show command...")
        result = runner.invoke(cli, ['show', 'auth.jwt'])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output snippet: {result.output[:100]}...")
        assert result.exit_code == 0
        assert 'auth.jwt' in result.output
        print("   ✅ Show successful")

        # Test 4: Search for documents
        print("\n4. Testing search command...")
        result = runner.invoke(cli, ['search', 'jwt'])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        assert 'auth.jwt' in result.output
        print("   ✅ Search successful")

        # Test 5: List documents
        print("\n5. Testing list command...")
        result = runner.invoke(cli, ['list'])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        assert 'auth.jwt' in result.output
        print("   ✅ List successful")

        # Test 6: Append to document
        print("\n6. Testing append command...")
        result = runner.invoke(cli, [
            'append',
            'auth.jwt',
            'Added token blacklist feature for enhanced security'
        ])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        print("   ✅ Append successful")

        # Test 7: Record a decision
        print("\n7. Testing record-decision command...")
        result = runner.invoke(cli, [
            'record-decision',
            'auth.jwt',
            'Token expiration strategy',
            'Use 15-minute access tokens for security balance'
        ])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        print("   ✅ Record decision successful")

        # Test 8: Update the document
        print("\n8. Testing update via store --update...")
        result = runner.invoke(cli, [
            'store',
            'auth.jwt',
            'Enhanced JWT authentication system with blacklist',
            'JWT system with token blacklist and 15-minute expiration for enhanced security.',
            '--update'
        ])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        print("   ✅ Update successful")

        # Test 9: Check version history
        print("\n9. Testing log command...")
        result = runner.invoke(cli, ['log', 'auth.jwt'])
        print(f"   Exit code: {result.exit_code}")
        print(f"   Output: {result.output.strip()}")
        assert result.exit_code == 0
        print("   ✅ Log successful")

        # Test 10: Status command
        print("\n10. Testing status command...")
        result = runner.invoke(cli, ['status'])
        print(f"    Exit code: {result.exit_code}")
        print(f"    Output: {result.output.strip()}")
        assert result.exit_code == 0
        print("    ✅ Status successful")

        print("\n🎉 All tests passed! aidocs CLI is working correctly.")
        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Cleanup
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    success = test_basic_workflow()
    sys.exit(0 if success else 1)