
# GitHub-Compatible Document Template

## Overview
This template is designed for maximum compatibility with GitHub automations, bots, and documentation tools. It uses clear section headers, tables, and checklists that are easily parsed by scripts and CI/CD workflows. It is also aligned with SmartAIPlatform's coding, automation, and environment standards.

---

# <Document Title>

## Overview
<Brief summary of the document's purpose>

## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)
- [Environment](#environment)
- [Automation & CI/CD](#automation--cicd)
- [Configuration](#configuration)
- [Best Practices](#best-practices)
- [Change History](#change-history)

## Sections
### Section 1
<Content>

### Section 2
<Content>

## Environment
- Describe any required environment variables, .env file usage, and setup scripts.
- State that only one .env file at root is allowed and all scripts must use the centralized setup_env.py.


## Automation & CI/CD
All code and documentation must pass the following automated checks before merge:

- **Formatting & Linting:**
	- black (formatting)
	- flake8, pylint (linting)
	- isort (import sorting)
	- codespell (spell checking)
- **Type Checking:**
	- mypy
- **Security:**
	- bandit (Python security)
	- safety, pip-audit (dependency vulnerabilities)
	- gitleaks (secret scanning)
- **Testing & Coverage:**
	- pytest (unit/integration tests)
	- pytest-cov (minimum 90% coverage)
- **Modularity & Structure:**
	- check_py_length.py (file length)
	- check_python_utilities.py (Python-only scripts)
	- check_dependencies.py (dependency presence)
- **Complexity & Duplication:**
	- radon (cyclomatic complexity)
	- flake8-cognitive-complexity
	- jscpd (code duplication)
	- vulture, autoflake (unused code/imports)
- **Config & Docs:**
	- yamllint (YAML)
	- markdownlint (Markdown)
	- jsonlint (JSON)
	- hadolint (Dockerfile)
- **Frontend (if present):**
	- eslint, prettier, stylelint
- **Service & Environment:**
	- setup_env.py (centralized env)
	- manage_services.py (service health)
- **Commit Message:**
	- gitlint (commit message style)

**Best Practices:**
- All contributors must run pre-commit locally before pushing.
- PRs will not be merged unless all checks pass in CI.
- All automation is defined in .pre-commit-config.yaml and .github/workflows/ci_enforce.yml.
- Add a CI status badge to README for visibility (recommended).

## Configuration
- List any configuration files (requirements.txt, Dockerfile, etc.) and their standards.
- Note that all dependencies must be in requirements.txt and all config must be centralized.

## Best Practices
- Summarize any coding, documentation, or operational best practices relevant to this document.
- Reference coding_and_modularization_standards.md and python_script_coding_rules.md as needed.

## Tasks & Checklists
- [ ] Task 1
- [ ] Task 2

## References
- [Link or reference]

## Change History
| Date       | Change            | Author        |
|------------|-------------------|--------------|
| YYYY-MM-DD | Initial version   | <Name>        |

---

# Notes for Automation
- Use Markdown tables for structured data.
- Use checklists for task tracking (GitHub recognizes and updates these automatically).
- Use clear, unique section headers for easy parsing by bots/scripts.
- Keep change history at the end for auditability.
- Use checklists for task tracking (GitHub recognizes and updates these automatically).
- Use clear, unique section headers for easy parsing by bots/scripts.
- Keep change history at the end for auditability.
