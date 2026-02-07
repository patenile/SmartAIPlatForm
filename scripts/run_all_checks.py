#!/usr/bin/env python3
"""
Master script to run all rule checks for SmartAIPlatform.
- Dynamically discovers check scripts in scripts/.
- Supports categories and CLI options for extensibility.
"""
import sys
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
import subprocess
from pathlib import Path
import re
import importlib.util
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor, as_completed

from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

# Define SCRIPT_DIR and CONFIG before discover_scripts()
SCRIPT_DIR = Path(__file__).parent
CONFIG = {
    "exclude": ["run_all_checks.py", "__init__.py"],
    "plugin_dir": SCRIPT_DIR / "plugins"
}

def discover_scripts():
    """Find all check scripts in scripts/ directory, excluding patterns."""
    scripts = [f for f in SCRIPT_DIR.iterdir() if f.is_file() and f.name.endswith('.py') and f.name not in CONFIG["exclude"]]
    # Discover plugins
    if CONFIG["plugin_dir"].exists():
        scripts += [f for f in CONFIG["plugin_dir"].iterdir() if f.is_file() and f.name.endswith('.py')]
    return sorted(scripts)

def get_script_category(script_path):
    try:
        with open(script_path, encoding='utf-8') as f:
            first40 = ''.join([next(f) for _ in range(40)])
        m = re.search(r'Category:\s*([\w-]+)', first40, re.IGNORECASE)
        if m:
            return m.group(1).strip().lower()
    except Exception:
        pass
    return 'uncategorized'

def build_category_map(scripts):
    cat_map = {}
    for script in scripts:
        cat = get_script_category(script)
        cat_map.setdefault(cat, []).append(script)
    return cat_map

def run_script(script, debug=False, autofix=False, dry_run=False):
    result = {
        "script": script.name,
        "category": get_script_category(script),
        "status": "",
        "output": ""
    }
    try:
        cmd = [sys.executable, str(script)]
        if debug:
            cmd.append("--debug")
        if autofix:
            cmd.append("--autofix")
        if dry_run:
            cmd.append("--dry-run")
        import time
        start = time.time()
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            result["status"] = "TIMEOUT"
            result["output"] = f"Script timed out after 180 seconds: {script.name}"
            return result
        elapsed = time.time() - start
        if elapsed > 60:
            print(f"[SLOW SCRIPT] {script.name} took {elapsed:.1f} seconds.")
        result["output"] = proc.stdout + proc.stderr
        if proc.returncode == 0:
            result["status"] = "PASS"
        else:
            result["status"] = "FAIL"
    except Exception as e:
        result["status"] = "ERROR"
        result["output"] = str(e)
    return result

def print_report(results, fmt="table", logger=None):
    headers = ["Script", "Category", "Status"]
    rows = [[r["script"], r["category"], r["status"]] for r in results]
    if fmt == "table":
        logger.info("\n" + tabulate(rows, headers, tablefmt="github"))
    elif fmt == "markdown":
        logger.info("\n" + tabulate(rows, headers, tablefmt="pipe"))
    elif fmt == "html":
        logger.info("\n" + tabulate(rows, headers, tablefmt="html"))
    else:
        for r in results:
            logger.info(f"{r['script']} [{r['category']}]: {r['status']}")

def print_full_failures(results, logger):
    for r in results:
        if r["status"] in ("FAIL", "ERROR"):
            logger.error(f"\n--- {r['script']} [{r['category']}] {r['status']} ---\n{r['output']}")

def main():
    parser = get_arg_parser()
    parser.description = "Run all or selected rule checks."
    parser.add_argument('--all', action='store_true', help='Run all check scripts (default)')
    parser.add_argument('--category', type=str, help='Run all checks in a category')
    parser.add_argument('--script', type=str, help='Run a specific script by name')
    parser.add_argument('--list', action='store_true', help='List available categories and scripts')
    parser.add_argument('--report', type=str, choices=["table", "markdown", "html", "plain"], default="table", help='Report format')
    parser.add_argument('--parallel', action='store_true', help='Run checks in parallel')
    parser.add_argument('--autofix', action='store_true', help='Pass --autofix to all rule scripts')
    parser.add_argument('--dry-run', action='store_true', help='Pass --dry-run to all rule scripts')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    try:
        scripts = discover_scripts()
        cat_map = build_category_map(scripts)
        if hasattr(args, 'list_categories') and args.list_categories:
            print("Available categories:")
            for cat in sorted(cat_map):
                print(f"  {cat}")
            sys.exit(0)
        if args.list:
            logger.info("Available categories:")
            for cat in sorted(cat_map):
                logger.info(f"  {cat}")
            logger.info("\nAvailable scripts:")
            for script in scripts:
                logger.info(f"  {script.name}")
            sys.exit(0)
        targets = []
        if args.script:
            match = [s for s in scripts if s.name == args.script]
            if not match:
                logger.error(f"Script not found: {args.script}")
                sys.exit(1)
            targets = match
        elif args.category:
            cat = args.category.strip().lower()
            if cat not in cat_map:
                logger.error(f"Category not found: {cat}")
                logger.error(f"Available: {', '.join(sorted(cat_map))}")
                sys.exit(1)
            targets = cat_map[cat]
        else:
            targets = scripts
        results = []
        if args.parallel and len(targets) > 1:
            with ThreadPoolExecutor() as executor:
                future_to_script = {executor.submit(run_script, s, args.debug, args.autofix, args.dry_run): s for s in targets}
                for future in as_completed(future_to_script):
                    results.append(future.result())
        else:
            for script in targets:
                results.append(run_script(script, args.debug, args.autofix, args.dry_run))
        print_report(results, fmt=args.report, logger=logger)
        print_full_failures(results, logger)
        # Custom exit codes: 0 if all pass, 1 if any fail, 2 if any error
        if any(r["status"] == "ERROR" for r in results):
            sys.exit(2)
        elif any(r["status"] == "FAIL" for r in results):
            sys.exit(1)
        else:
            sys.exit(0)
    except Exception as e:
        logger.error(f"Exception in run_all_checks: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
