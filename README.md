# SmartAIPlatform

## Overview
A generic, modular, and automation-ready platform for rapid application development with Python, Docker, and AI-driven automation.

## Quick Start
1. Copy `.env.example` to `.env` and fill in required values.
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment:
   ```sh
   python scripts/setup_env.py
   ```
4. Run all checks and tests:
   ```sh
   pre-commit run --all-files
   pytest
   ```
5. Build and run with Docker (optional):
   ```sh
   docker build -t smartaiplatform .
   docker run --env-file .env smartaiplatform
   ```

## Automation & CI/CD
- All code must pass pre-commit and CI checks before merge.
- See docs/github_compatible_doc_template.md for documentation standards.
- See docs/coding_and_modularization_standards.md for coding/modularity standards.
- See docs/python_script_coding_rules.md for Python script rules.

## Rule Checks: Dynamic, Categorized, and Extensible


All rule checks are run via the master script:

```sh
python scripts/run_all_checks.py [--all | --category <cat> | --script <name> | --list]
```

- `--all` (default): Run all check scripts in scripts/ (dynamic discovery)
- `--category <cat>`: Run all checks in a category (e.g., modularity, dependencies, environment, services, board)
- `--script <name>`: Run a specific script by filename (e.g., check_py_length.py)
- `--list`: List available categories and scripts

**How it works:**
- All check scripts in scripts/ are auto-discovered (no manual list maintenance)
- Each script declares its category in the docstring (e.g., `Category: modularity`)
- Categories and scripts are extensible: add a new script with a category tag and it is auto-included
- All errors are mapped to rules/fixes via scripts/rule_mapping.json for actionable feedback
- **All check scripts support `--autofix` and `--dry-run` options:**
   - `--autofix`: Attempts to automatically fix rule violations (where possible), or logs a clear message if not auto-fixable.
   - `--dry-run`: Previews what would be changed by auto-fix, without making any modifications.
   - These options are available for every check script, even if some only log a stub message for manual intervention.

**Examples:**
- Run all checks: `python scripts/run_all_checks.py`
- Run only modularity checks: `python scripts/run_all_checks.py --category modularity`
- Run dependency check: `python scripts/run_all_checks.py --script check_dependencies.py`
- List all categories/scripts: `python scripts/run_all_checks.py --list`
- Preview auto-fix for all rules (dry-run):
   ```sh
   python scripts/check_py_length.py --dry-run
   python scripts/check_shebang_and_imports.py --dry-run
   python scripts/check_dependencies.py --dry-run
   python scripts/check_python_utilities.py --dry-run
   python scripts/setup_env.py --dry-run
   python scripts/manage_services.py --dry-run
   python scripts/check_onboarding.py --dry-run
   python scripts/check_docstrings.py --dry-run
   ```
- Apply auto-fix for all rules (where possible):
   ```sh
   python scripts/check_py_length.py --autofix
   python scripts/check_shebang_and_imports.py --autofix
   python scripts/check_dependencies.py --autofix
   python scripts/check_python_utilities.py --autofix
   python scripts/setup_env.py --autofix
   python scripts/manage_services.py --autofix
   python scripts/check_onboarding.py --autofix
   python scripts/check_docstrings.py --autofix
   ```

See scripts/rule_mapping.json for rule-to-fix mapping. See docs/python_script_coding_rules.md for more on categories and extensibility.

## Rule Onboarding Wizard

To interactively enable, suppress, or configure rules for your project, run:

```bash
python3 scripts/rule_onboarding_wizard.py
```

This wizard will:
- List all available rules and their descriptions
- Let you select which rules to enable or suppress
- Allow you to override default settings for each rule
- Update `.smartai_rules.yaml` with your choices

Use `--dry-run` to preview changes without writing files.

## Rule Change Notification

To detect and notify about changes to rules (added, removed, or modified), run:

```bash
python3 scripts/notify_rule_change.py --slack --email
```

- Notifies via Slack and/or email if rule_mapping.json or .smartai_rules.yaml change.
- Use --update-snapshots to update the baseline after reviewing changes.

## Rule Deprecation/Upgrade Automation

To detect deprecated rules and suggest or apply upgrades, run:

```bash
python3 scripts/rule_deprecation_upgrade.py --slack --email --auto-upgrade
```

- Notifies if deprecated rules are in use and suggests upgrades.
- Use --auto-upgrade to migrate config to new rules if available.

## Rule Coverage Reporting

To see which files are covered by which rules, run:

```bash
python3 scripts/report_rule_coverage.py --report markdown
```

This generates a Markdown table showing rule coverage per file and per rule. See [docs/rule_coverage.md](docs/rule_coverage.md) for details and instructions.

## Automated Rule Impact Analysis

To analyze which files are affected by rule changes, run:

```bash
python3 scripts/rule_impact_analysis.py
```

- Reports which files are affected by each rule.
- Use `--rule <rule_name>` to analyze a specific rule.

## Automated Rule Documentation Sync

To check and update rule documentation, run:

```bash
python3 scripts/rule_doc_sync.py --fix
```

- Ensures docs/python_script_coding_rules.md matches rule_mapping.json.
- Notifies if documentation is out of sync; use --fix to auto-update.

## Advanced Features

- **Parallel Execution:** Use `--parallel` to run checks in parallel for speed.
- **Report Formats:** Use `--report markdown`, `--report html`, or `--report plain` for different output formats (default: table).
- **Plugin System:** Place external check scripts in `scripts/plugins/` and they will be auto-discovered and categorized.
- **Configurable Exclusion:** Exclude scripts from checks by adding their names to the `exclude` list in `run_all_checks.py`.
- **Custom Exit Codes:**
  - 0: All checks passed
  - 1: At least one check failed
  - 2: At least one check errored (script crash)

**Examples:**
- Run all checks in parallel, output Markdown:
  ```sh
  python scripts/run_all_checks.py --parallel --report markdown
  ```
- Run only service checks, output HTML:
  ```sh
  python scripts/run_all_checks.py --category services --report html
  ```
- Add a plugin: Place a Python script in `scripts/plugins/` with a `Category:` tag in the docstring.

## Environment
- Only one `.env` at root is allowed.
- All scripts/services must use `scripts/setup_env.py` for environment setup.
- Never commit secrets to the repo; use `.env.example` as a template.

## Configuration
- All dependencies in `requirements.txt`.
- Tool configs in `pyproject.toml`.
- Dockerfile for containerization.

## Contributing
- Run all pre-commit hooks before pushing.
- PRs will not be merged unless all checks pass in CI.

## License
MIT

## Rule Usage Analytics Dashboard

To generate a dashboard of rule usage and violation trends, run:

```bash
python3 scripts/rule_usage_analytics.py --update-dashboard
```

- Aggregates rule violations, auto-fix rates, and trends over time.
- Outputs a Markdown dashboard at docs/rule_usage_dashboard.md.

## Automated PR Feedback Bot

To post inline PR comments for rule violations, run:

```bash
python3 scripts/pr_feedback_bot.py --pr <PR_NUMBER>
```

- Requires GITHUB_TOKEN, GITHUB_REPOSITORY, and PR_NUMBER environment variables.
- Posts inline comments and a summary for rule violations on the pull request.

## Rule Exception Expiry/Review Automation

To track and review rule suppressions/overrides with expiry dates, run:

```bash
python3 scripts/rule_exception_review.py --slack --email --auto-remove
```

- Notifies if exceptions are due for review or expired.
- Use --auto-remove to clean up expired exceptions from config.
- Add 'until:YYYY-MM-DD' in suppression reason to set expiry.

## Cross-Repo Rule Consistency Checker

To check rule config consistency across multiple repos, run:

```bash
python3 scripts/cross_repo_rule_consistency.py --repos /path/to/other/repo1 /path/to/other/repo2
```

- Compares rule_mapping.json and .smartai_rules.yaml across repos.
- Reports inconsistencies and suggests sync actions.

## Rule Severity Levels & Enforcement Modes

To set or list severity/enforcement for rules, run:

```bash
python3 scripts/rule_severity_enforcement.py --list
python3 scripts/rule_severity_enforcement.py --set <RULE> <SEVERITY> <ENFORCEMENT>
```

- Severity: error, warning, info
- Enforcement: block, warn, log-only
- Updates rule_mapping.json for each rule

## Custom Rule Authoring SDK (CLI)

To create a new rule with script, test, and doc stubs, run:

```bash
python3 scripts/rule_authoring_sdk.py
```

- Guides you through rule creation (name, description, category)
- Generates a script, test stub, and doc entry
- Adds metadata to rule_mapping.json

## Rule Marketplace/Registry Integration

To list, import, or publish rules from/to the registry, run:

```bash
python3 scripts/rule_marketplace.py --list
python3 scripts/rule_marketplace.py --import-rule <RULE_SCRIPT>
python3 scripts/rule_marketplace.py --publish-rule <RULE_SCRIPT>
```

- Uses rule_registry/ as a local registry (can be extended to remote)
- Allows sharing and importing rule scripts

## Automated Rollback/Hotfix for Rule Failures

To auto-revert the last rule/config change if CI fails, run:

```bash
python3 scripts/rule_rollback_hotfix.py --auto-revert --notify --ci-log <CI_LOG_PATH>
```

- Detects failures via CI log or context
- Reverts last rule/config commit and notifies maintainers

## Rule Dependency Graph Visualization

To generate a visual dependency/conflict graph for rules, run:

```bash
python3 scripts/rule_dependency_graph.py --update-graph
```

- Outputs a Mermaid diagram to docs/rule_dependency_graph.md
- Add 'depends_on' and 'conflicts_with' fields in rule_mapping.json for relationships

## User/Team Ownership Mapping

To assign, list, or query rule/file ownership, run:

```bash
python3 scripts/rule_ownership_mapping.py --set-rule-owner <RULE> <OWNER>
python3 scripts/rule_ownership_mapping.py --set-file-owner <FILE> <OWNER>
python3 scripts/rule_ownership_mapping.py --list-rule-owners
python3 scripts/rule_ownership_mapping.py --list-file-owners
python3 scripts/rule_ownership_mapping.py --query <RULE_OR_FILE>
```

- Updates rule_mapping.json and file_ownership.json
- Enables targeted notifications and accountability

## Rule 'What-If' Simulator

To preview the impact of enabling/disabling rules, run:

```bash
python3 scripts/rule_what_if_simulator.py --enable <RULE1> <RULE2> --disable <RULE3>
```

- Shows which files and owners would be affected
- No changes are applied; simulation only

## Self-Documenting Rules

To auto-generate rule documentation from code and config, run:

```bash
python3 scripts/self_documenting_rules.py --update-docs
```

- Extracts docstrings and examples from rule scripts
- Updates docs/python_script_coding_rules.md

## Rule Drift Detection

To detect if code is drifting from enforced rules, run:

```bash
python3 scripts/rule_drift_detection.py --slack --email
```

- Compares current violations to a historical baseline
- Notifies if drift increases or new violations appear
- Use --update-baseline to set the current state as the new baseline

## Automated Rule Performance Profiling

To profile rule runtimes and detect bottlenecks, run:

```bash
python3 scripts/rule_performance_profiling.py --profile <RULE_SCRIPT>
python3 scripts/rule_performance_profiling.py --aggregate --alert-threshold 2.0
```

- Tracks and reports runtime of each rule
- Aggregates and alerts if a rule is slow

## Rule Explainability/AI Suggestions

To get AI-powered explanations and suggestions for rule violations, run:

```bash
python3 scripts/rule_explainability_ai.py --explain
python3 scripts/rule_explainability_ai.py --violation '{"rule": "check_docstrings", "message": "Missing docstring in function foo"}'
```

- Uses AI to explain violations and suggest fixes (placeholder, can integrate with OpenAI or local LLM)
- Logs explanations to logs/rule_explanations.jsonl

## Automated Rule Tuning

To suggest or auto-tune rule thresholds based on violation patterns, run:

```bash
python3 scripts/rule_auto_tuning.py --suggest
python3 scripts/rule_auto_tuning.py --apply
```

- Analyzes violation data and suggests optimal thresholds
- Can auto-update rule_mapping.json for tunable rules

## Rule Adoption Analytics

To analyze rule adoption and get recommendations, run:

```bash
python3 scripts/rule_adoption_analytics.py --report
```

- Tracks rule usage by violations and owners

## Automated Rule Migration Assistant

To suggest or auto-migrate deprecated rules, run:

```bash
python3 scripts/rule_migration_assistant.py --suggest
python3 scripts/rule_migration_assistant.py --apply
```

- Scans for deprecated rules and maps to new best practices
- Updates .smartai_rules.yaml as needed

## Rule Feedback Loop

To submit or summarize feedback on rules, run:

```bash
python3 scripts/rule_feedback_loop.py --submit <RULE> <FEEDBACK> [--user <USER>]
python3 scripts/rule_feedback_loop.py --summary
```

- Collects developer feedback on rules (e.g., "too strict", "false positive")
- Aggregates and summarizes feedback for maintainers

## Rule-Aware Code Review Assignment

To suggest reviewers for changed files based on rule/file ownership, run:

```bash
python3 scripts/rule_aware_review_assignment.py --assign
```

- Assigns PR reviewers based on file and rule ownership
- Uses file_ownership.json and rule_mapping.json

## Automated Security Patch for Rule Scripts

To scan and auto-patch rule scripts for security issues, run:

```bash
python3 scripts/rule_security_patch.py --scan --patch --notify
```

- Scans for dangerous code (eval, exec, os.system, subprocess, etc.)
- Auto-patches/comment out dangerous lines and notifies maintainers

## Rule-Based Release Gates

**Script:** `scripts/rule_release_gates.py`

- Blocks releases if critical rules are violated, based on rule severity and enforcement metadata.
- Integrates with CI/CD to enforce release gates.
- Supports `--enforce` to block release, and `--override` to allow release with escalation.
- Logs all actions and violations.

**Usage:**

```sh
python scripts/rule_release_gates.py --enforce
# To override and allow release despite violations:
python scripts/rule_release_gates.py --enforce --override
```

## Rule Visualization Dashboard

**Script:** `scripts/rule_visualization_dashboard.py`

- Interactive web dashboard for rule analytics, coverage, drift, and trends.
- Visualizes rule violations, performance, adoption, and more using Dash/Plotly.
- Tabs for Violations, Performance, Adoption, and Drift.

**Usage:**

```sh
python scripts/rule_visualization_dashboard.py
```

- Open http://localhost:8050 in your browser to view the dashboard.
