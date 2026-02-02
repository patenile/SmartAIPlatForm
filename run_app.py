#!/usr/bin/env python3
"""
run_app.py: Orchestrates the full SmartAIPlatForm application.
- Starts backend, frontend, and infrastructure as needed.
- Can be extended to support dev, test, or prod modes.
"""
import subprocess
import sys
import argparse

COMPONENTS = [
    ("Infrastructure (docker-compose)", ["docker-compose", "up", "-d"]),
    ("Backend", ["python3", "-m", "backend"]),
    ("Frontend", ["npm", "start", "--prefix", "frontend"]),
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
    subprocess.check_call([sys.executable, "scripts/setup_env.py"])

def cleanup_env():
    subprocess.check_call([sys.executable, "scripts/cleanup.py"])

def main():
    parser = argparse.ArgumentParser(description="SmartAIPlatForm Orchestrator")
    parser.add_argument("command", choices=["run", "setup", "cleanup"], help="Action to perform")
    args = parser.parse_args()

    if args.command == "run":
        run_components()
    elif args.command == "setup":
        setup_env()
    elif args.command == "cleanup":
        cleanup_env()

if __name__ == "__main__":
    main()
