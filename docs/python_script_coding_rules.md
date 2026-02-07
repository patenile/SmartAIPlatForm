# Centralized Logging and Argument Parsing

## Logging
- All scripts must use the centralized logger from `scripts/central_logger.py`.
- No `print` statements are allowed; use `logger.info`, `logger.error`, `logger.warning`, or `logger.debug` as appropriate.
- All exceptions and errors must be logged and handled gracefully.

## Argument Parsing
- All scripts must use the centralized argument parser from `scripts/central_args.py`.
- No script should instantiate its own `argparse.ArgumentParser` directly.
- The `--debug` option must be supported and propagated to all scripts and technologies (Python, Docker, APIs, services, etc.).

## Error Handling
- All system exceptions must be caught and logged using the centralized logger.
- Scripts should exit with a non-zero code on error, after logging the error.

## Example Usage

```python
from scripts.central_logger import get_logger
from scripts.central_args import get_arg_parser

def main():
  parser = get_arg_parser()
  args = parser.parse_args()
  logger = get_logger(debug=args.debug)
  try:
    # ... script logic ...
    logger.info("Script ran successfully.")
  except Exception as e:
    logger.error(f"Exception: {e}")
    sys.exit(1)
```

## Enforcement
- These rules are enforced by code review, pre-commit, and CI checks.

## Auto-fix and Dry-run Support

- All rule check scripts support the `--autofix` and `--dry-run` options.
  - `--autofix`: Attempts to automatically fix rule violations (where possible), or logs a clear message if not auto-fixable.
  - `--dry-run`: Previews what would be changed by auto-fix, without making any modifications.
- These options are available for every check script, even if some only log a stub message for manual intervention.
- Pre-commit and CI can invoke these options for automated or previewed fixes.

### Example Usage

```sh
# Preview auto-fix for all rules (dry-run):
python scripts/check_py_length.py --dry-run
python scripts/check_shebang_and_imports.py --dry-run
python scripts/check_dependencies.py --dry-run
python scripts/check_python_utilities.py --dry-run
python scripts/setup_env.py --dry-run
python scripts/manage_services.py --dry-run
python scripts/check_onboarding.py --dry-run
python scripts/check_docstrings.py --dry-run

# Apply auto-fix for all rules (where possible):
python scripts/check_py_length.py --autofix
python scripts/check_shebang_and_imports.py --autofix
python scripts/check_dependencies.py --autofix
python scripts/check_python_utilities.py --autofix
python scripts/setup_env.py --autofix
python scripts/manage_services.py --autofix
python scripts/check_onboarding.py --autofix
python scripts/check_docstrings.py --autofix
```

See each script's help (`--help`) for details on what is auto-fixable.

## Rule Onboarding Wizard

- Use the onboarding wizard to interactively enable, suppress, or configure rules for your project.
- Run:

  ```bash
  python3 scripts/rule_onboarding_wizard.py
  ```
- The wizard updates `.smartai_rules.yaml` with your selections.
- Use `--dry-run` to preview changes.

## Rule Coverage Reporting

- Rule coverage is tracked per file and per rule.
- To generate a coverage report, run:

  ```bash
  python3 scripts/report_rule_coverage.py --report markdown
  ```
- The report shows which rules are checked, skipped, or suppressed for each file.
- See [docs/rule_coverage.md](rule_coverage.md) for the latest report and instructions.

## Rule Change Notification

- To detect and notify about rule changes, run:

  ```bash
  python3 scripts/notify_rule_change.py --slack --email
  ```
- Notifies via Slack and/or email if rules are added, removed, or modified.
- Use `--update-snapshots` to update the baseline after reviewing changes.

## Rule Deprecation/Upgrade Automation

- To detect deprecated rules and suggest or apply upgrades, run:

  ```bash
  python3 scripts/rule_deprecation_upgrade.py --slack --email --auto-upgrade
  ```
- Notifies if deprecated rules are in use and suggests upgrades.
- Use `--auto-upgrade` to migrate config to new rules if available.

## Automated Rule Impact Analysis

- To analyze which files are affected by rule changes, run:

  ```bash
  python3 scripts/rule_impact_analysis.py
  ```
- Reports which files are affected by each rule.
- Use `--rule <rule_name>` to analyze a specific rule.

## Rule Usage Analytics Dashboard

- To generate a dashboard of rule usage and violation trends, run:

  ```bash
  python3 scripts/rule_usage_analytics.py --update-dashboard
  ```
- Outputs a Markdown dashboard at docs/rule_usage_dashboard.md.

## Rule Exception Expiry/Review Automation

- To track and review rule suppressions/overrides with expiry dates, run:

  ```bash
  python3 scripts/rule_exception_review.py --slack --email --auto-remove
  ```
- Notifies if exceptions are due for review or expired.
- Use `--auto-remove` to clean up expired exceptions from config.
- Add 'until:YYYY-MM-DD' in suppression reason to set expiry.

## Rule Dependency Graph Visualization

- To generate a visual dependency/conflict graph for rules, run:

  ```bash
  python3 scripts/rule_dependency_graph.py --update-graph
  ```
- Outputs a Mermaid diagram to docs/rule_dependency_graph.md
- Add 'depends_on' and 'conflicts_with' fields in rule_mapping.json for relationships

## Rule List

- This section is auto-synced with rule_mapping.json.
- Run `python3 scripts/rule_doc_sync.py --fix` to update.

---

# Python Script Coding Rules for SmartAIPlatform

## Overview
These rules are mandatory for every Python script in the project, including new code, bugfixes, and refactoring. All rules are enforced by pre-commit hooks, CI workflows, and code review. They are aligned with SmartAIPlatform’s modularization, automation, and environment standards.

---

## Required Coding Rules

1. **Linting & Formatting**
   - All code must pass flake8 and pylint (no errors, only allowed warnings).
   - Use black for code formatting (enforced via pre-commit).
   - isort must be used for import sorting.
   - bandit must pass for security linting.
   - codespell for spell checking.

2. **Docstrings & Comments**
   - Every module, class, and function must have a docstring.
   - Public functions/classes must have clear parameter and return descriptions.
   - All files must start with the standard header comment (see coding_and_modularization_standards.md).

3. **Type Annotations**
   - All function signatures must use type hints.
   - mypy must pass with no errors.

4. **File Structure & Modularity**
   - Max 350 lines per file (±10%).
   - No “God” files: split large files into focused modules.
   - Use feature-based or layered structure as described in coding_and_modularization_standards.md.
   - Every Python file must start with a shebang (#!) as the first line (e.g., `#!/usr/bin/env python3`).
   - All import statements must be grouped at the top of the file, immediately after the shebang and any module docstring/comments.

5. **Testing & Coverage**
   - All new/changed code must have corresponding unit tests.
   - Tests must pass locally and in CI.
   - Minimum 90% test coverage enforced by CI.

6. **Security & Best Practices**
   - No hardcoded secrets or credentials.
   - Use environment variables for sensitive data (via setup_env.py and .env at root only).
   - Use centralized install/service scripts for any setup or service management.
   - All utility/setup scripts must be Python only.

7. **Dependencies & Configuration**
   - All dependencies must be listed in requirements.txt.
   - No unused imports or packages (checked by autoflake/vulture).
   - No duplicate or missing dependencies (checked by check_dependencies.py).

8. **Function Quality**
   - Functions must be maintainable, testable, scalable, secure, and have proper info/debug/error/warning messages.
   - Cyclomatic complexity and function length are checked by CI.

---

## Enforcement
- All rules are enforced via pre-commit hooks and CI workflows.
- Commits or PRs that fail any rule will be blocked until fixed.
- Code review must verify adherence to these rules.

---

## Example Pre-commit Config Snippet

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-pylint
    rev: v3.1.0
    hooks:
      - id: pylint
  - repo: https://github.com/pre-commit/mirrors-isort
    rev: v5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
  - repo: https://github.com/PyCQA/bandit
    rev: v1.7.7
    hooks:
      - id: bandit
  - repo: https://github.com/codespell-project/codespell
    rev: v2.2.6
    hooks:
      - id: codespell
  - repo: local
    hooks:
      - id: check-py-length
        name: Check Python file length
        entry: python scripts/check_py_length.py
        language: system
        types: [python]
        pass_filenames: false
```

---

> For any new script or bugfix, run all pre-commit hooks and tests before pushing or opening a PR.

## Automated PR Feedback Bot

- To post inline PR comments for rule violations, run:

  ```bash
  python3 scripts/pr_feedback_bot.py --pr <PR_NUMBER>
  ```
- Requires GITHUB_TOKEN, GITHUB_REPOSITORY, and PR_NUMBER environment variables.
- Posts inline comments and a summary for rule violations on the pull request.
- Links to documentation for each rule.

## Cross-Repo Rule Consistency Checker

- To check rule config consistency across multiple repos, run:

  ```bash
  python3 scripts/cross_repo_rule_consistency.py --repos /path/to/other/repo1 /path/to/other/repo2
  ```
- Compares rule_mapping.json and .smartai_rules.yaml across repos.
- Reports inconsistencies and suggests sync actions.

## Rule Severity Levels & Enforcement Modes

- To set or list severity/enforcement for rules, run:

  ```bash
  python3 scripts/rule_severity_enforcement.py --list
  python3 scripts/rule_severity_enforcement.py --set <RULE> <SEVERITY> <ENFORCEMENT>
  ```
- Severity: error, warning, info
- Enforcement: block, warn, log-only
- Updates rule_mapping.json for each rule

## Custom Rule Authoring SDK (CLI)

- To create a new rule with script, test, and doc stubs, run:

  ```bash
  python3 scripts/rule_authoring_sdk.py
  ```
- Guides you through rule creation (name, description, category)
- Generates a script, test stub, and doc entry
- Adds metadata to rule_mapping.json

## Automated Rollback/Hotfix for Rule Failures

- To auto-revert the last rule/config change if CI fails, run:

  ```bash
  python3 scripts/rule_rollback_hotfix.py --auto-revert --notify --ci-log <CI_LOG_PATH>
  ```
- Detects failures via CI log or context
- Reverts last rule/config commit and notifies maintainers

## Rule 'What-If' Simulator

- To preview the impact of enabling/disabling rules, run:

  ```bash
  python3 scripts/rule_what_if_simulator.py --enable <RULE1> <RULE2> --disable <RULE3>
  ```
- Shows which files and owners would be affected
- No changes are applied; simulation only

## User/Team Ownership Mapping

- To assign, list, or query rule/file ownership, run:

  ```bash
  python3 scripts/rule_ownership_mapping.py --set-rule-owner <RULE> <OWNER>
  python3 scripts/rule_ownership_mapping.py --set-file-owner <FILE> <OWNER>
  python3 scripts/rule_ownership_mapping.py --list-rule-owners
  python3 scripts/rule_ownership_mapping.py --list-file-owners
  python3 scripts/rule_ownership_mapping.py --query <RULE_OR_FILE>
  ```
- Updates rule_mapping.json and file_ownership.json
- Enables targeted notifications and accountability

## Self-Documenting Rules

- To auto-generate rule documentation from code and config, run:

  ```bash
  python3 scripts/self_documenting_rules.py --update-docs
  ```
- Extracts docstrings and examples from rule scripts
- Updates this file with extracted info

## Rule Drift Detection

- To detect if code is drifting from enforced rules, run:

  ```bash
  python3 scripts/rule_drift_detection.py --slack --email
  ```
- Compares current violations to a historical baseline
- Notifies if drift increases or new violations appear
- Use `--update-baseline` to set the current state as the new baseline

## Automated Rule Tuning

- To suggest or auto-tune rule thresholds based on violation patterns, run:

  ```bash
  python3 scripts/rule_auto_tuning.py --suggest
  python3 scripts/rule_auto_tuning.py --apply
  ```
- Analyzes violation data and suggests optimal thresholds
- Can auto-update rule_mapping.json for tunable rules

## Rule Feedback Loop

- To submit or summarize feedback on rules, run:

  ```bash
  python3 scripts/rule_feedback_loop.py --submit <RULE> <FEEDBACK> [--user <USER>]
  python3 scripts/rule_feedback_loop.py --summary
  ```
- Collects developer feedback on rules (e.g., "too strict", "false positive")
- Aggregates and summarizes feedback for maintainers

## Automated Security Patch for Rule Scripts

- To scan and auto-patch rule scripts for security issues, run:

  ```bash
  python3 scripts/rule_security_patch.py --scan --patch --notify
  ```
- Scans for dangerous code (eval, exec, os.system, subprocess, etc.)
- Auto-patches/comment out dangerous lines and notifies maintainers

## Rule-Based Release Gates

- **Purpose:** Prevents releases if critical rules are violated, enforcing strict quality and compliance.
- **How it works:**
    - Scans the latest rule violations log for any critical rules (severity: error, enforcement: block).
    - If any are found, the release is blocked unless an explicit `--override` is provided (for escalation/approval workflows).
    - Integrates with CI/CD for automated enforcement.
- **Script:** `scripts/rule_release_gates.py`
- **Typical usage:**
    - `python scripts/rule_release_gates.py --enforce` (blocks release if critical violations exist)
    - `python scripts/rule_release_gates.py --enforce --override` (allows release with override, logs warning)
- **Best practices:**
    - Use in pre-release or deployment CI jobs.
    - Require justification for overrides and log them for audit.

## Rule Visualization Dashboard

- **Purpose:** Provides an interactive web dashboard for all rule analytics, coverage, drift, and trends.
- **How it works:**
    - Loads logs for violations, performance, adoption, and drift.
    - Visualizes data using Dash/Plotly with interactive charts and tabs.
    - Enables deep insights into rule health, adoption, and issues.
- **Script:** `scripts/rule_visualization_dashboard.py`
- **Typical usage:**
    - `python scripts/rule_visualization_dashboard.py` (then open http://localhost:8050)
- **Best practices:**
    - Use for regular monitoring and reporting.
    - Extend with new tabs/metrics as new automations are added.

- **None**: Custom rule: None (category: custom)