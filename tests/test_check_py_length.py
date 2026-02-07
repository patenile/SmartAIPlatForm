#!/usr/bin/env python3
import subprocess
import sys

def test_check_py_length_runs():
    result = subprocess.run([
        sys.executable, "scripts/check_py_length.py", "--dry-run"
    ], capture_output=True, text=True)
    assert result.returncode == 0
    assert "PASS" in result.stdout or "No violations" in result.stdout or result.stdout
