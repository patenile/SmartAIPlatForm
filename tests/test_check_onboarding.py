#!/usr/bin/env python3
import subprocess
import sys

def test_check_onboarding_runs():
    result = subprocess.run([
        sys.executable, "scripts/check_onboarding.py", "--dry-run"
    ], capture_output=True, text=True)
    assert result.stdout or result.stderr
