import subprocess
import sys
import random
import string
from pathlib import Path
import pytest
import os

SCRIPTS = [
    "setup_env.py",
    "cleanup.py",
    "check_links.py",
]
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
RUN_APP = Path(__file__).parent.parent / "run_app.py"

# Systematic and random argument generation for CLI fuzzing
def random_arg():
    return ''.join(random.choices(string.ascii_letters + string.digits + '-_', k=random.randint(1, 12)))

def arg_combinations():
    # Systematic: known flags, help, nonsense
    combos = [
        ["--help"],
        ["-h"],
        ["--unknown"],
        [random_arg()],
        ["--help", random_arg()],
        ["--version"],
        [],
    ]
    # Add random combos
    for _ in range(10):
        combos.append([random_arg() for _ in range(random.randint(1, 3))])
    return combos

@pytest.mark.parametrize("script_name", SCRIPTS)
def test_script_cli_fuzzing(script_name):
    script_path = SCRIPTS_DIR / script_name
    assert script_path.exists(), f"{script_path} does not exist"
    for args in arg_combinations():
        try:
            result = subprocess.run([sys.executable, str(script_path)] + args, capture_output=True, text=True, timeout=8)
        except subprocess.TimeoutExpired:
            pytest.fail(f"Timeout running {script_path} with args {args}")
        # Should not crash (no traceback)
        if "traceback" in result.stderr.lower():
            print(f"\n--- FAIL: {script_path} args={args} ---\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}")
        assert "traceback" not in result.stderr.lower(), f"Traceback for {script_path} with args {args}:\n{result.stderr}"
        # Should print something or exit with usage error
        if not (result.stdout.strip() != "" or result.returncode in (0, 1)):
            print(f"\n--- FAIL: {script_path} args={args} ---\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}")
        assert result.stdout.strip() != "" or result.returncode in (0, 1), f"No output for {script_path} with args {args}"

# --- Interactive CLI fuzzing tests ---
import pexpect

@pytest.mark.parametrize("script_name", SCRIPTS)
def test_script_interactive_cli_fuzzing(script_name):
    script_path = SCRIPTS_DIR / script_name
    prompt = f"{script_name.split('.')[0]}>"
    for args in arg_combinations():
        # Only use first arg for interactive CLI
        if args:
            try:
                child = pexpect.spawn(f"{sys.executable} {script_path}", timeout=10)
                child.expect(prompt, timeout=5)
                child.sendline(args[0])
                child.expect([pexpect.EOF, prompt], timeout=5)
                child.sendline("exit")
                child.expect("Exiting interactive mode.", timeout=5)
                child.terminate()
            except (pexpect.TIMEOUT, pexpect.EOF) as exc:
                pytest.fail(f"pexpect error for {script_path} with arg {args[0]}: {exc}")

@pytest.mark.parametrize("cmd", ["setup", "cleanup", "run", "--help", "-h", "--unknown", random_arg()])
def test_run_app_interactive_cli_fuzzing(cmd):
    prompt = "run_app>"
    try:
        child = pexpect.spawn(f"{sys.executable} {RUN_APP}", timeout=10)
        child.expect(prompt, timeout=5)
        child.sendline(cmd)
        child.expect([pexpect.EOF, prompt], timeout=5)
        child.sendline("exit")
        child.expect("Exiting interactive mode.", timeout=5)
        child.terminate()
    except (pexpect.TIMEOUT, pexpect.EOF) as exc:
        pytest.fail(f"pexpect error for run_app.py with cmd {cmd}: {exc}")

@pytest.mark.parametrize("cmd", ["setup", "cleanup", "run", "--help", "-h", "--unknown", random_arg()])
def test_run_app_cli_fuzzing(cmd):
    try:
        result = subprocess.run([sys.executable, str(RUN_APP), cmd], capture_output=True, text=True, timeout=8)
    except subprocess.TimeoutExpired:
        pytest.fail(f"Timeout running run_app.py with cmd {cmd}")
    if "traceback" in result.stderr.lower():
        print(f"\n--- FAIL: run_app.py cmd={cmd} ---\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}")
    assert "traceback" not in result.stderr.lower(), f"Traceback for run_app.py with cmd {cmd}:\n{result.stderr}"
    if not (result.stdout.strip() != "" or result.returncode in (0, 1)):
        print(f"\n--- FAIL: run_app.py cmd={cmd} ---\nSTDERR:\n{result.stderr}\nSTDOUT:\n{result.stdout}")
    assert result.stdout.strip() != "" or result.returncode in (0, 1), f"No output for run_app.py with cmd {cmd}"

@pytest.mark.parametrize("script_name", SCRIPTS)
def test_script_interactive_advanced_scenarios(script_name):
    script_path = SCRIPTS_DIR / script_name
    env = os.environ.copy()
    prompt = f"{script_name.split('.')[0]}>"
    # Advanced: send invalid, edge-case, and unicode commands
    child = pexpect.spawn(f"{sys.executable} {script_path}", timeout=20, env=env)
    child.expect(prompt, timeout=5)
    # Valid commands
    for cmd in ["help", "status", "info", "version", "diagnostics", "reset"]:
        child.sendline(cmd)
        child.expect([pexpect.EOF, prompt], timeout=7)
    # Invalid command
    child.sendline("foobar")
    child.expect("Unknown command", timeout=5)
    # Unicode command
    child.sendline("帮助")
    child.expect([pexpect.EOF, prompt], timeout=7)
    # Edge-case: empty input
    child.sendline("")
    child.expect([pexpect.EOF, prompt], timeout=7)
    child.sendline("exit")
    child.expect("Exiting interactive mode.", timeout=5)
    child.terminate()
