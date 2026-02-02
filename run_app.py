#!/usr/bin/env python3
"""
run_app.py: Orchestrates the full SmartAIPlatForm application.
- Starts backend, frontend, and infrastructure as needed.
- Can be extended to support dev, test, or prod modes.
"""
import subprocess
import sys
import argparse
from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.resolve()
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

COMPONENTS = [
    ("Infrastructure (docker-compose)", ["docker-compose", "up", "-d"]),
    ("Backend", [sys.executable, "-m", "backend"]),
    ("Frontend", ["npm", "start", "--prefix", str(PROJECT_ROOT / "frontend")]),
]

def run_components():
    print("Starting SmartAIPlatForm...")
    for name, cmd in COMPONENTS:
        print(f"Launching {name}...")
        try:
            subprocess.Popen(cmd)
        except Exception as e:
            print(f"Failed to start {name}: {e}")
    print("All components launched. Monitor logs for status.")

def setup_env():
    setup_path = SCRIPTS_DIR / "setup_env.py"
    subprocess.check_call([sys.executable, str(setup_path)])

def cleanup_env():
    cleanup_path = SCRIPTS_DIR / "cleanup.py"
    subprocess.check_call([sys.executable, str(cleanup_path)])

def main():
    parser = argparse.ArgumentParser(description="SmartAIPlatForm Orchestrator")
    parser.add_argument("command", nargs="?", default="run", choices=["run", "setup", "cleanup"], help="Action to perform")
    args = parser.parse_args()

    if args.command == "run":
        run_components()
    elif args.command == "setup":
        setup_env()
    elif args.command == "cleanup":
        cleanup_env()

if __name__ == "__main__":
    main()
