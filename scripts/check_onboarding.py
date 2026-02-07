
#!/usr/bin/env python3
"""
Check for onboarding essentials: .env, config, and onboarding docs.
Category: onboarding
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config, get_file_rule_settings, is_rule_suppressed

def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix missing onboarding essentials')
    parser.add_argument('--dry-run', action='store_true', help='Preview auto-fix changes')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    config = load_rule_config()
    script_path = Path(__file__).resolve()
    settings = get_file_rule_settings(script_path, config)
    # Rule suppression (temporary/permanent)
    suppressed, reason = is_rule_suppressed('check_onboarding', config, script_path)
    if suppressed:
        logger.info(f"[suppressed] Skipping check_onboarding for {script_path} (reason: {reason})")
        return
    if 'check_onboarding' in (settings.get('skip_rules') or []):
        logger.info(f"[selective enforcement] Skipping check_onboarding for {script_path}")
        return
    try:
        root = Path(__file__).parent.parent
        essentials = [".env.example", "README.md", "docs/coding_and_modularization_standards.md", "docs/python_script_coding_rules.md"]
        missing = [f for f in essentials if not (root / f).exists()]
        if args.autofix or args.dry_run:
            if missing:
                for f in missing:
                    if args.dry_run:
                        logger.info(f"[dry-run] Would create or restore missing onboarding file: {f}")
                    else:
                        logger.info(f"Auto-fix: Please manually create or restore {f}")
            else:
                logger.info("No onboarding essentials missing.")
            return
        if missing:
            logger.error("Missing onboarding essentials:")
            for f in missing:
                logger.error(f"  - {f}")
            sys.exit(1)
        logger.info("All onboarding essentials are present.")
    except Exception as e:
        logger.error(f"Exception in check_onboarding: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
