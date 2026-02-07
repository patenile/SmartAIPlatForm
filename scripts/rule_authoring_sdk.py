#!/usr/bin/env python3
"""
Custom Rule Authoring SDK (CLI Wizard)
- Guides users to create new rule scripts with templates and test harnesses
- Adds rule metadata to rule_mapping.json
- Optionally generates doc and test stubs
Category: automation
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
# from scripts.{script_name} import main

RULES_DIR = Path(__file__).parent
RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
TESTS_DIR = Path(__file__).parent.parent / "tests"
DOCS_PATH = Path(__file__).parent.parent / "docs/python_script_coding_rules.md"

RULE_TEMPLATE = '''#!/usr/bin/env python3
"""
{description}
Category: {category}
"""

def main():
    parser = get_arg_parser()
    parser.add_argument('--autofix', action='store_true', help='Auto-fix violations')
    parser.add_argument('--dry-run', action='store_true', help='Dry run')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    # TODO: Implement rule logic here
    logger.info("Rule '{name}' executed.")

if __name__ == "__main__":
    main()
'''

TEST_TEMPLATE = '''import pytest

def test_{name}_basic():
    # TODO: Add test logic for {name}
    assert True
'''

def load_rule_mapping():
    if RULE_MAPPING_PATH.exists():
        with open(RULE_MAPPING_PATH) as f:
            return json.load(f)
    return {}

def save_rule_mapping(mapping):
    with open(RULE_MAPPING_PATH, "w") as f:
        json.dump(mapping, f, indent=2)

def prompt(msg, default=None):
    if default:
        msg = f"{msg} [{default}]"
    val = input(msg + ": ").strip()
    return val if val else default

def main():
    parser = get_arg_parser()
    parser.add_argument('--name', type=str, help='Rule name (snake_case)')
    parser.add_argument('--category', type=str, default='custom', help='Rule category')
    parser.add_argument('--description', type=str, help='Rule description')
    parser.add_argument('--no-test', action='store_true', help='Skip test stub generation')
    parser.add_argument('--no-doc', action='store_true', help='Skip doc stub generation')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    name = args.name or prompt("Rule name (snake_case)")
    category = args.category or prompt("Category", default='custom')
    description = args.description or prompt("Description", default=f"Custom rule: {name}")
    script_name = f"check_{name}.py"
    script_path = RULES_DIR / script_name
    if script_path.exists():
        logger.error(f"Script {script_name} already exists.")
        sys.exit(1)
    # Create rule script
    script_code = RULE_TEMPLATE.format(name=name, description=description, category=category)
    script_path.write_text(script_code)
    logger.info(f"Created rule script: {script_path}")
    # Add to rule_mapping.json
    mapping = load_rule_mapping()
    mapping[name] = {
        "description": description,
        "category": category,
        "script": script_name,
        "severity": "error",
        "enforcement": "block"
    }
    save_rule_mapping(mapping)
    logger.info(f"Added {name} to rule_mapping.json")
    # Create test stub
    if not args.no_test:
        test_code = TEST_TEMPLATE.format(name=name, script_name=script_name.replace('.py',''))
        test_path = TESTS_DIR / f"test_{name}.py"
        test_path.write_text(test_code)
        logger.info(f"Created test stub: {test_path}")
    # Add doc stub
    if not args.no_doc:
        doc_line = f"- **{name}**: {description} (category: {category})"
        with open(DOCS_PATH, "a") as f:
            f.write(f"\n{doc_line}")
        logger.info(f"Added doc stub to {DOCS_PATH}")
    logger.info("Rule authoring complete.")

if __name__ == "__main__":
    main()
