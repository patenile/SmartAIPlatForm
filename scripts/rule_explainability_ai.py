#!/usr/bin/env python3
"""
Rule Explainability/AI Suggestions
- Uses AI to explain rule violations and suggest context-aware fixes
- Integrates with OpenAI API (or local LLM) for explanations
- Can be called from other scripts or as a CLI tool
Category: automation
"""
import sys
import json
import os
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

VIOLATION_LOG = Path(__file__).parent.parent / "logs/rule_violations.jsonl"
EXPLANATION_LOG = Path(__file__).parent.parent / "logs/rule_explanations.jsonl"

# Placeholder for AI call (replace with real API integration)
def ai_explain_violation(violation):
    # Example: Use OpenAI, Azure, or local LLM
    # Here, just return a dummy explanation and suggestion
    rule = violation.get('rule')
    message = violation.get('message', '')
    return {
        "explanation": f"The rule '{rule}' was violated because: {message}. (AI explanation placeholder)",
        "suggestion": f"To fix this, follow the best practices for '{rule}'. (AI suggestion placeholder)"
    }

def main():
    parser = get_arg_parser()
    parser.add_argument('--explain', action='store_true', help='Explain all recent rule violations')
    parser.add_argument('--violation', type=str, help='Explain a specific violation (as JSON string)')
    args = parser.parse_args()
    logger = get_logger(debug=args.debug)
    explanations = []
    if args.violation:
        v = json.loads(args.violation)
        result = ai_explain_violation(v)
        logger.info(f"Explanation: {result['explanation']}")
        logger.info(f"Suggestion: {result['suggestion']}")
        explanations.append({**v, **result})
    elif args.explain:
        if not VIOLATION_LOG.exists():
            logger.info("No violations to explain.")
            return
        with open(VIOLATION_LOG) as f:
            for line in f:
                if line.strip():
                    v = json.loads(line)
                    result = ai_explain_violation(v)
                    logger.info(f"Violation: {v}")
                    logger.info(f"Explanation: {result['explanation']}")
                    logger.info(f"Suggestion: {result['suggestion']}")
                    explanations.append({**v, **result})
    if explanations:
        with open(EXPLANATION_LOG, "a") as f:
            for e in explanations:
                f.write(json.dumps(e) + "\n")
        logger.info(f"Logged {len(explanations)} explanations to {EXPLANATION_LOG}")
    if not (args.explain or args.violation):
        parser.print_help()

if __name__ == "__main__":
    main()
