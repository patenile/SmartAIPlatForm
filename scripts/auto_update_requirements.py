#!/usr/bin/env python3

import sys, os
import subprocess
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
"""
Auto-update requirements.txt if dependencies change (pip freeze).
Category: dependencies
"""

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def main():
    parser = get_arg_parser()
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    try:
        req_file = Path(__file__).parent.parent / "requirements.txt"
        # Get current frozen requirements
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True)
        frozen = result.stdout.strip()
        with open(req_file, "r", encoding="utf-8") as f:
            current = f.read().strip()
        if frozen != current:
            logger.info("[auto-update] requirements.txt is out of sync. Updating...")
            with open(req_file, "w", encoding="utf-8") as f:
                f.write(frozen + "\n")
            logger.info("requirements.txt updated. Please commit the changes.")
        else:
            logger.info("requirements.txt is up to date.")
    except Exception as e:
        logger.error(f"Exception in auto_update_requirements: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
