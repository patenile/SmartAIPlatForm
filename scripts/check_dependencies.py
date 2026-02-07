#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pkgutil
import subprocess
from pathlib import Path
import json
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed
"""
Check for missing dependencies: all imports must be in requirements.txt.
Fails if any import is missing from requirements.txt.
Category: dependencies
"""

def print_rule_and_fix(logger):
    mapping_path = Path(__file__).parent / "rule_mapping.json"
    if mapping_path.exists():
        with open(mapping_path) as f:
            rules = json.load(f)
        rule = rules.get("check_dependencies", {})
        logger.info(f"Rule: {rule.get('rule','')}")
        logger.info(f"See: {rule.get('doc','')}")
        logger.info(f"Suggested fix: {rule.get('fix','')}")

def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix missing dependencies in requirements.txt')
    parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
    parser.add_argument('--requirements', type=str, help='Path to requirements.txt (overrides env REQUIREMENTS_PATH)')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    script_path = Path(__file__).resolve()
    settings = get_file_rule_settings(script_path, config)
    suppressed, reason = is_rule_suppressed('check_dependencies', config, script_path)
    requirements_path = args.requirements if args.requirements else os.environ.get('REQUIREMENTS_PATH')
    if not requirements_path:
        requirements_path = str(Path(__file__).parent.parent / "requirements.txt")
    if suppressed:
        logger.info(f"[suppressed] Skipping check_dependencies for {script_path} (reason: {reason})")
        return
    if 'check_dependencies' in (settings.get('skip_rules') or []):
        logger.info(f"[selective enforcement] Skipping check_dependencies for {script_path}")
        return
    try:
        reqs = set()
        with open(requirements_path) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    reqs.add(line.split('==')[0].strip().lower())
        # Use pipreqs CLI to detect imports
        try:
            pipreqs_cmd = ["pipreqs", "scripts", "--force", "--savepath", "pipreqs.txt"]
            if args.debug:
                pipreqs_cmd.append("--debug")
            subprocess.run(pipreqs_cmd, check=True)
            missing_pkgs = []
            with open("pipreqs.txt") as f:
                for line in f:
                    pkg = line.split('==')[0].strip()
                    if pkg and pkg.lower() not in reqs:
                        missing_pkgs.append(pkg)
            if args.autofix or args.dry_run:
                if missing_pkgs:
                    if args.dry_run:
                        logger.info(f"[dry-run] Would add missing dependencies to requirements.txt: {', '.join(missing_pkgs)}")
                    else:
                        with open(Path(__file__).parent.parent / "requirements.txt", "a", encoding="utf-8") as reqf:
                            for pkg in missing_pkgs:
                                reqf.write(f"{pkg}\n")
                        logger.info(f"Added missing dependencies to requirements.txt: {', '.join(missing_pkgs)}")
                else:
                    logger.info("No missing dependencies to auto-fix.")
                return
            if missing_pkgs:
                for pkg in missing_pkgs:
                    logger.error(f"Missing dependency in requirements.txt: {pkg}")
                print_rule_and_fix(logger)
                sys.exit(1)
        except Exception as e:
            logger.error(f"ERROR running pipreqs: {e}")
            print_rule_and_fix(logger)
            sys.exit(1)
        logger.info("All dependencies are listed in requirements.txt.")
    except Exception as e:
        logger.error(f"Exception in check_dependencies: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
