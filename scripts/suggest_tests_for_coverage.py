
#!/usr/bin/env python3
"""
Suggest files to add tests for if coverage drops below threshold.
Category: testing
"""
import sys
import re
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

def main():
    parser = get_arg_parser()
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    try:
        # Read pytest coverage report from stdin
        report = sys.stdin.read()
        missing = re.findall(r'MISSING\s+(.+)', report)
        if missing:
            logger.warning("Coverage below threshold. Consider adding tests for:")
            for f in missing:
                logger.warning(f"  - {f}")
        else:
            logger.info("Coverage is sufficient.")
    except Exception as e:
        logger.error(f"Exception in suggest_tests_for_coverage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
