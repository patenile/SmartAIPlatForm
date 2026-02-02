# Tooling & Automation Implementation Log

**Last Updated:** February 1, 2026

This document tracks all tools, scripts, and automations implemented in the SmartAIPlatForm project. For each, it records the purpose, installation/activation steps, and how/when it is used.

---

## Table of Contents
1. [Overview](#overview)
2. [Implemented Tools & Scripts](#implemented-tools--scripts)
3. [Directory Organization](#directory-organization)
4. [Change History](#change-history)

---

## Overview
This log provides a traceable record of all project-level tools, scripts, and automations, including their rationale and usage. It supports onboarding, audits, and future maintenance.

---

## Implemented Tools & Scripts

| Tool/Script         | Location                | Purpose/Why         | How/When Used                | Install/Activate Steps                |
|---------------------|------------------------|---------------------|------------------------------|---------------------------------------|
| pre-commit          | .pre-commit-config.yaml| Run checks before every commit (e.g., lint, link check) | On every git commit                  | `pre-commit install`                  |
| check_links.py      | scripts/check_links.py  | Check all Markdown docs for broken links | Via pre-commit, CI, or manually       | `pip install requests` (for CI), auto-run by pre-commit and GitHub Action |
| setup_env.py        | scripts/setup_env.py    | Ensures .venv exists, creates with python3.12 if missing, installs/checks required packages | `python run_app.py setup` or manually | Requires python3.12, requirements.txt, .venv |
| cleanup.py          | scripts/cleanup.py      | Cleans up all installed packages and removes .venv | `python run_app.py cleanup` or manually | Requires .venv present |
| run_app.py          | run_app.py              | CLI orchestrator for setup, cleanup, and app run | `python run_app.py [setup|cleanup|run]` | Python 3.12+ |
| check-links.yml     | .github/workflows/      | CI automation for link checking         | On every push/PR to docs/scripts      | GitHub Actions auto-runs              |
| Docker/Colima       | docker-compose.yml      | Containerized local dev, cross-platform | On local dev, CI, prod                | See infrastructure.md                 |
| GitHub Actions      | .github/workflows/      | CI/CD for build, test, deploy           | On every push/PR                      | GitHub auto-runs                      |
| ...                 | ...                    | ...                                     | ...                                  | ...                                   |

---

### Example: setup_env.py
- **Purpose:** Ensures a consistent Python environment for all scripts and backend code. Creates .venv with python3.12 if missing, installs/checks all required packages from requirements.txt.
- **How it works:**
  - Checks if .venv exists; if not, creates it with python3.12.
  - Checks if all packages in requirements.txt are installed; installs any missing ones.
  - Errors if requirements.txt is missing or packages are not satisfied after install.
- **How/When Used:**
  - Run automatically via `python run_app.py setup` or manually as needed.
- **Install/Activate:**
  - Requires python3.12 and requirements.txt in project root.

### Example: cleanup.py
- **Purpose:** Cleans up the Python environment for a fresh start or before switching branches/major upgrades.
- **How it works:**
  - Uninstalls all packages in .venv.
  - Removes the .venv directory.
  - Warns if .venv is currently active in the shell.
- **How/When Used:**
  - Run via `python run_app.py cleanup` or manually as needed.
- **Install/Activate:**
  - Requires .venv present in project root.

### Example: run_app.py CLI
- **Purpose:** Single entrypoint for orchestrating setup, cleanup, and app execution.
- **How it works:**
  - `python run_app.py setup` runs environment setup.
  - `python run_app.py cleanup` runs environment cleanup.
  - `python run_app.py run` launches all app components (infra, backend, frontend).
- **How/When Used:**
  - Used for onboarding, automation, and local development.
- **Install/Activate:**
  - Requires Python 3.12+ and all scripts in place.
- **Purpose:** Ensures all Markdown documentation links (internal and external) are valid, preventing broken navigation and improving project quality.
- **How it works:**
  - Scans all docs/*.md files for links.
  - Checks if internal file links exist and if external URLs are reachable.
  - Reports any broken/missing links.
- **How/When Used:**
  - Runs automatically before every commit (via pre-commit).
  - Runs in CI on every push/PR (via GitHub Actions).
  - Can be run manually: `python scripts/check_links.py`.
- **Install/Activate:**
  - Add to pre-commit config and run `pre-commit install`.
  - Ensure `requests` is installed for Python.

---

## Directory Organization

- `/scripts/` — All project-level automation, validation, and utility scripts (e.g., check_links.py, future tools)
- `/backend/` — Backend application code (API, business logic, etc.)
- `/frontend/` — Frontend application code (React, UI, etc.)
- `/infra/` — Infrastructure-as-code (e.g., Terraform, deployment scripts)
- `/docs/` — All documentation and markdown files
- `/tests/` — (Optional) Standalone test utilities/scripts
- `/run_app.py` — Single entrypoint to orchestrate the full application (calls backend, frontend, infra, etc.)
- `/docker-compose.yml` — Container orchestration for local/dev
- `/.github/` — GitHub Actions workflows and automation

> **Best Practice:** The root directory should only contain orchestration/entrypoint scripts (e.g., run_app.py), config files, and top-level folders for each major component.

---

## Change History
| Date | Change | Author |
|------|--------|--------|
| 2026-02-01 | Initial creation, added pre-commit, check_links.py, directory plan | GitHub Copilot |
| 2026-02-01 | Added setup_env.py, cleanup.py, run_app.py CLI integration, and updated documentation | GitHub Copilot |
