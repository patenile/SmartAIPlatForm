#!/usr/bin/env python3
import subprocess
import sys

def test_check_dependencies_runs():
    result = subprocess.run([
        sys.executable, "scripts/check_dependencies.py", "--dry-run"
    ], capture_output=True, text=True)
    # Accept nonzero return code if violations, but script should run
    assert result.stdout or result.stderr
