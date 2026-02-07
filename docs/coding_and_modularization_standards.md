# Centralized Logging and Argument Parsing (2026 Update)

## Logging
- All scripts and services must use the centralized logger (`scripts/central_logger.py`).
- No `print` statements are allowed anywhere in the codebase.
- Use logger tags: `info`, `debug`, `error`, `warning` for all output.

## Argument Parsing
- All scripts must use the centralized argument parser (`scripts/central_args.py`).
- No script should create its own `argparse.ArgumentParser`.
- The `--debug` option must be supported and propagated to all scripts, Docker, APIs, backend, frontend, configuration, services, PostgreSQL, and any other technology.

## Error Handling
- All exceptions and system errors must be caught and logged using the centralized logger.
- No unhandled exceptions should be allowed; scripts must exit gracefully on error.

## Example

See `docs/python_script_coding_rules.md` for code examples and enforcement details.
# SmartAIPlatform Modularization & Coding Standards

## Overview
This document defines the modularization strategies, coding standards, and enforcement mechanisms for all Python code in the SmartAIPlatform project. Adhering to these guidelines ensures maintainability, scalability, and ease of onboarding for new contributors.

---

## Environment Setup Rules & Best Practices

- Only one `.env` file is allowed, and it must be located at the project root.
- All environment variables must be loaded via the centralized `scripts/setup_env.py` script.
- No script, service, or tool should load or define environment variables except through `setup_env.py`.
- Any new environment variable must be added to `.env` at root and referenced in `setup_env.py`.
- If a `.env` file is found outside the root, CI and setup_env.py will fail.
- For secrets in production, use GitHub Actions secrets or a secure vault—never commit secrets to `.env` or the repository.
- All scripts and services must source/setup the environment by calling `python scripts/setup_env.py` before execution.

## Modularization Strategies

1. **Single Responsibility Principle**
   - Each file/module should implement one class, service, or a small set of closely related functions.

2. **Layered Structure**
   - Organize code into layers: models/, services/, controllers/, utils/, config/.

3. **Feature-Based Modules**
   - Group files by feature (e.g., user/, auth/, db/, api/) rather than by type.

4. **Avoid “God” Files**
   - Split large scripts into smaller, focused modules. Import as needed.

5. **Reusable Utilities**
   - Place shared helpers/utilities in a dedicated utils/ or common/ directory.

6. **Explicit Public API**
   - Use __init__.py to control what’s exposed from a package.

7. **Documentation**
   - Each module must have a docstring explaining its purpose and usage.

---

## Enforced Constraints

- **File Length:** Max 350 lines per Python file (±10% tolerance).
- **Header Comment:** Every Python file must start with the following header:

```python
# MODULE CONSTRAINTS:
# - Max 350 lines (±10%)
# - Single responsibility
# - Modular: split if growing too large
# - Update this header if refactoring
```

- **Docstring:** Each file must have a module-level docstring after the header.

---

## Enforcement Mechanisms

- **Pre-commit Hook:**
  - Checks for file length and header comment.
- **CI/CD Integration:**
  - Blocks merges if constraints are violated.
- **Linting/Static Analysis:**
  - Use flake8/pylint and custom plugins for additional checks.
- **Code Review:**
  - Reviewers must verify adherence to these standards.

---

## Coding Template (Python)

```python
# MODULE CONSTRAINTS:
# - Max 350 lines (±10%)
# - Single responsibility
# - Modular: split if growing too large
# - Update this header if refactoring

"""
Module Purpose: <Describe what this module does>
Usage: <How to use this module>
"""

# ...import statements...

# ...module code...

# ...if __name__ == "__main__": (optional)...
```

---

## Document Template (for new docs)

```
# <Document Title>

## Overview
<Brief summary of the document's purpose>

## Table of Contents
1. ...
2. ...

## Details
<Main content sections>

## References
- ...

## Change History
| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Initial version | <Name> |
```

---

## Review Checklist
- [ ] File length within limit
- [ ] Header comment present
- [ ] Module-level docstring present
- [ ] Follows modularization strategy
- [ ] Directory structure by feature/layer
- [ ] Doc template used for new docs

---

> For questions or suggestions, update this document and notify the team.
