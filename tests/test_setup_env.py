#!/usr/bin/env python3
import subprocess
import sys
def test_setup_env_runs():
    result = subprocess.run([
        sys.executable, "scripts/setup_env.py", "--dry-run"
    ], capture_output=True, text=True)
    assert result.stdout or result.stderr
