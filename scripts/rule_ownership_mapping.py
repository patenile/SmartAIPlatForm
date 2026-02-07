#!/usr/bin/env python3
"""
User/Team Ownership Mapping
- Assigns rule and file ownership for targeted notifications and accountability
- Updates rule_mapping.json and a new file_ownership.json
- Provides CLI to set, list, and query ownership
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
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
FILE_OWNERSHIP_PATH = Path(__file__).parent.parent / "file_ownership.json"


def load_json(path):
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    parser = get_arg_parser()
    parser.add_argument('--set-rule-owner', nargs=2, metavar=('RULE', 'OWNER'), help='Assign owner to a rule')
    parser.add_argument('--set-file-owner', nargs=2, metavar=('FILE', 'OWNER'), help='Assign owner to a file')
    parser.add_argument('--list-rule-owners', action='store_true', help='List rule owners')
    parser.add_argument('--list-file-owners', action='store_true', help='List file owners')
    parser.add_argument('--query', type=str, help='Query owner for a rule or file')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    # Rule ownership
    mapping = load_json(RULE_MAPPING_PATH)
    if args.set_rule_owner:
        rule, owner = args.set_rule_owner
        if rule not in mapping:
            logger.error(f"Rule '{rule}' not found.")
            sys.exit(1)
        mapping[rule]['owner'] = owner
        save_json(RULE_MAPPING_PATH, mapping)
        logger.info(f"Set owner of rule '{rule}' to {owner}")
    elif args.list_rule_owners:
        logger.info("Rule | Owner")
        logger.info("-----|------")
        for rule, meta in mapping.items():
            logger.info(f"{rule} | {meta.get('owner','-')}")
    # File ownership
    file_owners = load_json(FILE_OWNERSHIP_PATH)
    if args.set_file_owner:
        file, owner = args.set_file_owner
        file_owners[file] = owner
        save_json(FILE_OWNERSHIP_PATH, file_owners)
        logger.info(f"Set owner of file '{file}' to {owner}")
    elif args.list_file_owners:
        logger.info("File | Owner")
        logger.info("-----|------")
        for file, owner in file_owners.items():
            logger.info(f"{file} | {owner}")
    # Query
    if args.query:
        if args.query in mapping:
            logger.info(f"Rule '{args.query}' owner: {mapping[args.query].get('owner','-')}")
        elif args.query in file_owners:
            logger.info(f"File '{args.query}' owner: {file_owners[args.query]}")
        else:
            logger.info(f"No owner found for '{args.query}'")
    if not any([args.set_rule_owner, args.set_file_owner, args.list_rule_owners, args.list_file_owners, args.query]):
        parser.print_help()

if __name__ == "__main__":
    main()
