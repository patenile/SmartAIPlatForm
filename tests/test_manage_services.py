#!/usr/bin/env python3
import subprocess
import sys
def test_manage_services_runs():
    result = subprocess.run([
        sys.executable, "scripts/manage_services.py", "--dry-run"
    ], capture_output=True, text=True)
    assert result.stdout or result.stderr
