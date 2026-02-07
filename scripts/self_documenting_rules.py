#!/usr/bin/env python3
"""
Self-Documenting Rules
- Auto-generates human-friendly documentation/examples from rule code and config
- Updates docs/python_script_coding_rules.md with extracted docstrings, usage, and examples
Category: automation
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import ast
from pathlib import Path
import os
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULES_DIR = Path(__file__).parent
RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
DOCS_PATH = Path(__file__).parent.parent / "docs/python_script_coding_rules.md"


def extract_docstring_and_examples(script_path):
    try:
        with open(script_path) as f:
            tree = ast.parse(f.read())
        docstring = ast.get_docstring(tree) or ""
        # Find example code in docstring (lines starting with 'Example:' or code blocks)
        example = ""
        for line in docstring.splitlines():
            if line.strip().lower().startswith('example:'):
                example = line.strip()[8:].strip()
        return docstring, example
    except Exception:
        return "", ""

def main():
    parser = get_arg_parser()
    parser.add_argument('--update-docs', action='store_true', help='Update rule documentation with extracted info')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = json.load(open(RULE_MAPPING_PATH))
    lines = ["# Python Script Coding Rules\n"]
    for rule, meta in mapping.items():
        script = meta.get('script')
        if not script:
            continue
        script_path = RULES_DIR / script
        doc, example = extract_docstring_and_examples(script_path)
        lines.append(f"## {rule}\n")
        lines.append(f"**Description:** {meta.get('description','')}")
        if doc:
            lines.append(f"\n**Docstring:**\n{doc}")
        if example:
            lines.append(f"\n**Example:**\n{example}")
        lines.append("")
    if args.update_docs:
        DOCS_PATH.write_text('\n'.join(lines))
        logger.info(f"Documentation updated: {DOCS_PATH}")
    else:
        print('\n'.join(lines))

if __name__ == "__main__":
    main()
