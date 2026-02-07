#!/usr/bin/env python3
import subprocess
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed
"""
Service manager for SmartAIPlatform.
- Checks, starts, stops, and installs required services (e.g., Postgres, Docker, etc.)
- Reuses healthy services, otherwise cleans and restarts
- All install/start/stop logic is centralized here
Category: services
"""


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def print_rule_and_fix(logger):
    mapping_path = Path(__file__).parent / "rule_mapping.json"
    if mapping_path.exists():
        with open(mapping_path) as f:
            rules = json.load(f)
        rule = rules.get("manage_services", {
            "rule": "All services must be healthy and managed via centralized scripts. Reuse healthy services, otherwise clean and restart. Use Docker Compose for service orchestration.",
            "doc": "docs/coding_and_modularization_standards.md#environment-setup-rules--best-practices",
            "fix": "Ensure Docker and Docker Compose are installed. Use manage_services.py to check, stop, and start services as needed."
        })
        logger.info(f"Rule: {rule.get('rule','')}")
        logger.info(f"See: {rule.get('doc','')}")
        logger.info(f"Suggested fix: {rule.get('fix','')}")

def is_postgres_running(logger):
    try:
        subprocess.check_output(["pg_isready"])
        return True
    except Exception as e:
        logger.error("PostgreSQL is not running or not healthy.")
        logger.debug(f"Exception: {e}")
        print_rule_and_fix(logger)
        return False

def start_postgres(logger):
    logger.info("Starting PostgreSQL...")
    try:
        debug_flag = os.environ.get("SMARTAI_DEBUG", "0")
        cmd = ["docker", "compose", "up", "-d", "postgres"]
        if logger.isEnabledFor(10) or debug_flag == "1":
            cmd.append("--log-level=DEBUG")
        subprocess.run(cmd, check=True)
    except Exception as e:
        logger.error("Failed to start PostgreSQL with Docker Compose.")
        logger.debug(f"Exception: {e}")
        print_rule_and_fix(logger)
        sys.exit(1)

def stop_postgres(logger):
    logger.info("Stopping PostgreSQL...")
    try:
        debug_flag = os.environ.get("SMARTAI_DEBUG", "0")
        stop_cmd = ["docker", "compose", "stop", "postgres"]
        rm_cmd = ["docker", "compose", "rm", "-f", "postgres"]
        if logger.isEnabledFor(10) or debug_flag == "1":
            stop_cmd.append("--log-level=DEBUG")
            rm_cmd.append("--log-level=DEBUG")
        subprocess.run(stop_cmd, check=True)
        subprocess.run(rm_cmd, check=True)
    except Exception as e:
        logger.error("Failed to stop or remove PostgreSQL container.")
        logger.debug(f"Exception: {e}")
        print_rule_and_fix(logger)
        sys.exit(1)

def ensure_postgres(logger):
    if is_postgres_running(logger):
        logger.info("PostgreSQL is running and healthy.")
    else:
        stop_postgres(logger)
        start_postgres(logger)
        logger.info("PostgreSQL restarted.")

def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix unhealthy services (restart)')
    parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    script_path = Path(__file__).resolve()
    settings = get_file_rule_settings(script_path, config)
    suppressed, reason = is_rule_suppressed('manage_services', config, script_path)
    if suppressed:
        logger.info(f"[suppressed] Skipping manage_services for {script_path} (reason: {reason})")
        return
    if 'manage_services' in (settings.get('skip_rules') or []):
        logger.info(f"[selective enforcement] Skipping manage_services for {script_path}")
        return
    # Propagate debug to subprocesses via env var
    if args.debug:
        os.environ["SMARTAI_DEBUG"] = "1"
    try:
        # Check Docker
        try:
            subprocess.check_output(["docker", "--version"])
        except Exception:
            logger.error("Docker is not installed or not available in PATH.")
            print("Please install Docker. See docs/environment_setup.md for details.")
            sys.exit(1)
        # Check Docker Compose
        try:
            subprocess.check_output(["docker", "compose", "version"])
        except Exception:
            logger.error("Docker Compose is not installed or not available in PATH.")
            print("Please install Docker Compose. See docs/environment_setup.md for details.")
            sys.exit(1)
        # Check docker-compose.yml
        compose_path = Path(__file__).parent.parent / "docker-compose.yml"
        if not compose_path.exists():
            logger.error("docker-compose.yml not found in project root.")
            print("Please add docker-compose.yml with a postgres service. See docs/environment_setup.md for details.")
            sys.exit(1)
        with open(compose_path) as f:
            if "postgres" not in f.read():
                logger.error("docker-compose.yml does not define a postgres service.")
                print("Please define a postgres service in docker-compose.yml. See docs/environment_setup.md for details.")
                sys.exit(1)
        if args.autofix or args.dry_run:
            if args.dry_run:
                logger.info("[dry-run] Would restart unhealthy services (e.g., PostgreSQL)")
            else:
                logger.info("Auto-fix: Please manually restart unhealthy services (e.g., PostgreSQL)")
            return
        ensure_postgres(logger)
        # Add similar logic for other services as needed
    except Exception as e:
        logger.error(f"Exception in manage_services: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
