#!/usr/bin/env python3
"""
Automated Rule Documentation Sync
- Ensures rule documentation matches rule_mapping.json and .smartai_rules.yaml
- Updates docs/python_script_coding_rules.md and docs/rule_coverage.md as needed
- Notifies if documentation is out of sync
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
from pathlib import Path
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.rule_config import load_rule_config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
RULE_CONFIG_PATH = Path(__file__).parent.parent / ".smartai_rules.yaml"
DOC_RULES_PATH = Path(__file__).parent.parent / "docs/python_script_coding_rules.md"
DOC_COVERAGE_PATH = Path(__file__).parent.parent / "docs/rule_coverage.md"


def load_rule_mapping():
    if RULE_MAPPING_PATH.exists():
        with open(RULE_MAPPING_PATH) as f:
            return json.load(f)
    return {}

def update_rules_section(doc_path, rules):
    lines = doc_path.read_text().splitlines()
    start = None
    end = None
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('## rule list'):
            start = i
        if start is not None and line.strip() == '---':
            end = i
            break
    rule_lines = [f"- **{k}**: {v.get('description','')}{' (DEPRECATED)' if v.get('deprecated') else ''}" for k, v in rules.items()]
    if start is not None and end is not None:
        new_lines = lines[:start+1] + [''] + rule_lines + ['','---'] + lines[end+1:]
    else:
        # Append at end
        new_lines = lines + ['\n## Rule List',''] + rule_lines + ['','---']
    doc_path.write_text('\n'.join(new_lines))

def main():
    parser = get_arg_parser()
    parser.add_argument('--fix', action='store_true', help='Auto-fix documentation if out of sync')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = load_rule_mapping()
    # Check and sync python_script_coding_rules.md
    doc_path = DOC_RULES_PATH
    doc_text = doc_path.read_text() if doc_path.exists() else ''
    rule_lines = [f"- **{k}**: {v.get('description','')}{' (DEPRECATED)' if v.get('deprecated') else ''}" for k, v in mapping.items()]
    rules_section = '\n'.join(rule_lines)
    if rules_section not in doc_text:
        logger.info("Rule documentation is out of sync.")
        if args.fix:
            update_rules_section(doc_path, mapping)
            logger.info("Documentation updated.")
        else:
            logger.info("Run with --fix to update documentation.")
    else:
        logger.info("Rule documentation is up to date.")
    # (Optional) Sync rule_coverage.md or other docs as needed

if __name__ == "__main__":
    main()
