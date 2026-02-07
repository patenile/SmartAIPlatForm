#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
from dotenv import load_dotenv
import sys
import json
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
"""
Centralized environment setup script.
- Loads .env from project root
- Sets environment variables for all scripts/services
- Fails if .env is missing or found elsewhere
Category: environment
"""



def print_rule_and_fix(logger):
    mapping_path = Path(__file__).parent / "rule_mapping.json"
    if mapping_path.exists():
        with open(mapping_path) as f:
            rules = json.load(f)
        rule = rules.get("setup_env", {})
        logger.info(f"Rule: {rule.get('rule','')}")
        logger.info(f"See: {rule.get('doc','')}")
        logger.info(f"Suggested fix: {rule.get('fix','')}")

def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix .env location issues')
    parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    script_path = Path(__file__).resolve()
    settings = get_file_rule_settings(script_path, config)
    suppressed, reason = is_rule_suppressed('setup_env', config, script_path)
    if suppressed:
        logger.info(f"[suppressed] Skipping setup_env for {script_path} (reason: {reason})")
        return
    if 'setup_env' in (settings.get('skip_rules') or []):
        logger.info(f"[selective enforcement] Skipping setup_env for {script_path}")
        return
    try:
        root = Path(__file__).parent.parent
        env_path = root / ".env"
        # Check for .env elsewhere
        found_elsewhere = [p for p in root.rglob(".env") if p != env_path]
        if args.autofix or args.dry_run:
            if found_elsewhere:
                for p in found_elsewhere:
                    if args.dry_run:
                        logger.info(f"[dry-run] Would move {p} to {env_path}")
                    else:
                        logger.info(f"Auto-fix: Please manually move {p} to {env_path}")
            if not env_path.exists():
                if args.dry_run:
                    logger.info(f"[dry-run] Would create .env at {env_path}")
                else:
                    logger.info(f"Auto-fix: Please manually create .env at {env_path}")
            if not found_elsewhere and env_path.exists():
                logger.info("No .env location issues to auto-fix.")
            return
        for p in found_elsewhere:
            logger.error(f".env found outside root: {p}")
            print_rule_and_fix(logger)
            sys.exit(1)
        if not env_path.exists():
            logger.error(".env not found at project root.")
            print_rule_and_fix(logger)
            sys.exit(1)
        load_dotenv(dotenv_path=env_path)
        logger.info("Loaded environment from .env at root.")
    except Exception as e:
        logger.error(f"Exception in setup_env: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
