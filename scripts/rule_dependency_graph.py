#!/usr/bin/env python3
"""
Rule Dependency Graph Visualization
- Analyzes rule_mapping.json for dependencies/conflicts between rules
- Generates a Mermaid diagram for docs/rule_dependency_graph.md
Category: automation
"""
import sys
import json
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from pathlib import Path
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser
from scripts.renderMermaidDiagram import renderMermaidDiagram

RULE_MAPPING_PATH = Path(__file__).parent.parent / "rule_mapping.json"
GRAPH_MD = Path(__file__).parent.parent / "docs/rule_dependency_graph.md"


def load_rule_mapping():
    if RULE_MAPPING_PATH.exists():
        with open(RULE_MAPPING_PATH) as f:
            return json.load(f)
    return {}

def build_mermaid_graph(mapping):
    lines = ["graph TD"]
    for rule, meta in mapping.items():
        deps = meta.get('depends_on', [])
        conflicts = meta.get('conflicts_with', [])
        for dep in deps:
            lines.append(f"    {dep} --> {rule}")
        for conf in conflicts:
            lines.append(f"    {rule} -.-> {conf}")
    return '\n'.join(lines)

def main():
    parser = get_arg_parser()
    parser.add_argument('--update-graph', action='store_true', help='Update dependency graph markdown')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    mapping = load_rule_mapping()
    mermaid = build_mermaid_graph(mapping)
    if args.update_graph:
        md = f"# Rule Dependency Graph\n\n```mermaid\n{mermaid}\n```\n"
        GRAPH_MD.write_text(md)
        logger.info(f"Dependency graph updated: {GRAPH_MD}")
    else:
        print(mermaid)

if __name__ == "__main__":
    main()
