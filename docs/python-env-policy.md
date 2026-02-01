# Python Environment & venv Usage Policy

**Last Updated:** February 1, 2026

This document defines the policy and steps for Python environment management in SmartAIPlatForm. All Python scripts, automation, and backend code must use a single, isolated `.venv` created with Python 3.12+ at the project root.

---

## Table of Contents
1. [Rationale](#rationale)
2. [Setup Instructions](#setup-instructions)
3. [Usage Policy](#usage-policy)
4. [Configuration Updates](#configuration-updates)
5. [Change History](#change-history)

---

## Rationale
- Ensures all Python code (backend, scripts, automation) runs in a consistent, reproducible environment.
- Prevents dependency conflicts and system Python pollution.
- Simplifies onboarding and CI/CD setup.

---

## Setup Instructions

1. **Install Python 3.12+** (if not already):
   - macOS: `brew install python@3.12`
   - Linux: Use your package manager or download from python.org
2. **Create the venv at project root:**
   ```sh
   python3.12 -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   ```
3. **Install project dependencies:**
   - For backend: `pip install -r backend/requirements.txt` (or use poetry if configured)
   - For scripts: `pip install requests` (for check_links.py)
   - For dev tools: `pip install pre-commit`
4. **Activate venv for all work:**
   - Always run `source .venv/bin/activate` before running any Python command, script, or tool.

---

## Usage Policy
- All Python scripts (including scripts/check_links.py, backend, automation) must be run from the activated `.venv`.
- CI/CD and pre-commit must use `.venv/bin/python` as the interpreter.
- No global/system Python dependencies are allowed.
- Document any new Python dependency in the appropriate requirements file.

---

## Configuration Updates
- Update all scripts, pre-commit, and GitHub Actions to use `.venv/bin/python` instead of `python3` where possible.
- Document this policy in onboarding and tooling-log.md.
- Add a check to scripts/check_links.py to warn if not running inside `.venv`.

---

## Change History
| Date | Change | Author |
|------|--------|--------|
| 2026-02-01 | Initial creation, venv policy, config update plan | GitHub Copilot |
