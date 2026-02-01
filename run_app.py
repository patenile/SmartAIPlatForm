#!/usr/bin/env python3
"""
run_app.py: Orchestrates the full SmartAIPlatForm application.
- Starts backend, frontend, and infrastructure as needed.
- Can be extended to support dev, test, or prod modes.
"""
import subprocess
import sys

COMPONENTS = [
    ("Infrastructure (docker-compose)", ["docker-compose", "up", "-d"]),
    ("Backend", ["python3", "-m", "backend"]),
    ("Frontend", ["npm", "start", "--prefix", "frontend"]),
]

def main():
    print("Starting SmartAIPlatForm...")
    for name, cmd in COMPONENTS:
        print(f"Launching {name}...")
        try:
            subprocess.Popen(cmd)
        except Exception as e:
            print(f"Failed to start {name}: {e}")
    print("All components launched. Monitor logs for status.")

if __name__ == "__main__":
    main()
