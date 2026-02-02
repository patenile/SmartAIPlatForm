import sys
import os
import pytest
import pexpect
from pathlib import Path

SCRIPTS = [
    "setup_env.py",
    "cleanup.py",
    "check_links.py",
]
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"
RUN_APP = Path(__file__).parent.parent / "run_app.py"

@pytest.mark.integration
def test_run_app_interactive_help():
    child = pexpect.spawn(f"{sys.executable} {RUN_APP}", timeout=10)
    child.expect("run_app>", timeout=5)
    child.sendline("help")
    child.expect("Commands:", timeout=5)
    child.sendline("status")
    child.expect([pexpect.EOF, "run_app>"], timeout=5)
    child.sendline("exit")
    child.expect("Exiting interactive mode.", timeout=5)
    child.terminate()

@pytest.mark.parametrize("script_name", SCRIPTS)
def test_script_interactive_exit(script_name):
    script_path = SCRIPTS_DIR / script_name
    env = os.environ.copy()
    prompt = f"{script_name.split('.')[0]}>"
    if script_name == "cleanup.py":
        import tempfile
        temp_venv = tempfile.mkdtemp()
        env["SMARTAI_TEST_MODE"] = "1"
        env["SMARTAI_VENV_PATH"] = temp_venv
        child = pexpect.spawn(f"{sys.executable} {script_path}", timeout=10, env=env)
        child.expect(prompt, timeout=5)
        child.sendline("help")
        child.expect("Commands:", timeout=5)
        child.sendline("status")
        child.expect([pexpect.EOF, prompt], timeout=5)
        child.sendline("exit")
        child.expect("Exiting interactive mode.", timeout=5)
        child.terminate()
        import shutil
        shutil.rmtree(temp_venv)
    else:
        child = pexpect.spawn(f"{sys.executable} {script_path}", timeout=10)
        child.expect(prompt, timeout=5)
        child.sendline("help")
        child.expect("Commands:", timeout=5)
        child.sendline("status")
        child.expect([pexpect.EOF, prompt], timeout=5)
        child.sendline("exit")
        child.expect("Exiting interactive mode.", timeout=5)
        child.terminate()

import pexpect

@pytest.mark.parametrize("script_name", ["setup_env.py", "cleanup.py", "check_links.py"])
def test_script_interactive_all_commands(script_name):
    script_path = SCRIPTS_DIR / script_name
    env = os.environ.copy()
    prompt = f"{script_name.split('.')[0]}>"
    if script_name == "cleanup.py":
        import tempfile
        temp_venv = tempfile.mkdtemp()
        env["SMARTAI_TEST_MODE"] = "1"
        env["SMARTAI_VENV_PATH"] = temp_venv
        child = pexpect.spawn(f"{sys.executable} {script_path}", timeout=15, env=env)
        child.expect(prompt, timeout=5)
        child.sendline("help")
        child.expect("Commands:", timeout=5)
        for cmd in ["status", "info", "version", "diagnostics", "reset"]:
            child.sendline(cmd)
            child.expect([pexpect.EOF, prompt], timeout=7)
        child.sendline("exit")
        child.expect("Exiting interactive mode.", timeout=5)
        child.terminate()
        import shutil
        shutil.rmtree(temp_venv)
    else:
        child = pexpect.spawn(f"{sys.executable} {script_path}", timeout=15)
        child.expect(prompt, timeout=5)
        child.sendline("help")
        child.expect("Commands:", timeout=5)
        for cmd in ["status", "info", "version", "diagnostics", "reset"]:
            child.sendline(cmd)
            child.expect([pexpect.EOF, prompt], timeout=7)
        child.sendline("exit")
        child.expect("Exiting interactive mode.", timeout=5)
        child.terminate()

def test_run_app_interactive_all_commands():
    child = pexpect.spawn(f"{sys.executable} {RUN_APP}", timeout=15)
    child.expect("run_app>", timeout=5)
    child.sendline("help")
    child.expect("Commands:", timeout=5)
    for cmd in ["status", "info", "version", "diagnostics", "reset"]:
        child.sendline(cmd)
        child.expect([pexpect.EOF, "run_app>"], timeout=7)
    child.sendline("exit")
    child.expect("Exiting interactive mode.", timeout=5)
    child.terminate()
