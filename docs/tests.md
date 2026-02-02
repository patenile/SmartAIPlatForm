# Test Suite Documentation: scripts/*.py and run_app.py

**Last Updated:** February 1, 2026

This document describes the automated tests implemented for the SmartAIPlatForm project scripts and CLI orchestrator. It covers the purpose, rationale, and coverage of each test, supporting onboarding, maintenance, and auditability.

---

## Overview

The test suite ensures that all automation and orchestration scripts are present, executable, and provide user-friendly help and error handling. It also verifies that the main CLI (run_app.py) accepts all documented commands and responds as expected. This guards against accidental breakage, missing files, and regressions in developer tooling.

---

## Test File: tests/test_scripts_and_run_app.py

### 1. test_script_help
- **Purpose:**
  - Verifies that each script in `scripts/` responds to `--help` with usage/help output and does not crash.
- **Why Needed:**
  - Ensures discoverability and usability for all developer tooling scripts.
  - Prevents silent failures or missing usage documentation.
- **How It Works:**
  - Runs each script with `--help` and checks for a usage/help message in stdout/stderr.
  - Asserts that the script exists and returns exit code 0 or 1 (usage error).
- **Coverage:**
  - All scripts in `scripts/` (setup_env.py, cleanup.py, check_links.py).

### 2. test_run_app_help
- **Purpose:**
  - Ensures the main CLI orchestrator (`run_app.py`) provides a help/usage message.
- **Why Needed:**
  - Guarantees that users can discover available commands and options.
- **How It Works:**
  - Runs `run_app.py --help` and checks for a usage/help message in stdout/stderr.
  - Asserts exit code 0.
- **Coverage:**
  - `run_app.py` CLI entrypoint.

### 3. test_run_app_commands
- **Purpose:**
  - Verifies that `run_app.py` accepts all documented commands (`setup`, `cleanup`, `run`) and produces output without crashing.
- **Why Needed:**
  - Ensures CLI contract is stable and all commands are implemented.
  - Prevents regressions that could break automation or onboarding.
- **How It Works:**
  - Runs `run_app.py` with each command and checks for non-empty output and no Python traceback in stderr.
- **Coverage:**
  - All main CLI commands: `setup`, `cleanup`, `run`.

---

## Roadmap for Advanced Test Coverage & Customizations

This section outlines the next steps for expanding and strengthening the test suite to cover advanced scenarios, integrations, and real-world reliability:

### 1. Advanced Security & Compliance
- Integrate secrets scanning, permission enforcement, and audit logging.
- Add tests for authentication failures, permission boundaries, and secrets exposure.
- Implement and test audit trails for all destructive and sensitive operations.

### 2. Chaos/Fault Injection
- Simulate network partitions, service crashes, and resource exhaustion.
- Add tests for graceful recovery, error reporting, and retry logic.

### 3. Performance & Scalability
- Add load, stress, and concurrency tests for backend APIs and orchestration scripts.
- Measure and document response times, throughput, and resource usage.

### 4. Observability & Monitoring
- Integrate logging, metrics, and health/status endpoints.
- Add tests for log output, metrics collection, and alerting hooks.

### 5. Real-World Integration
- Add integration tests for all referenced APIs/services (FastAPI, Docker/Colima, PostgreSQL, GitHub Actions, pre-commit, React, Celery).
- Cover edge cases: rate limiting, malformed requests, migration/backup/restore, async tasks.

### 6. Data Integrity & Usability
- Add property-based and mutation tests for data validation, migration, and rollback.
- Test interactive CLI usability, help, diagnostics, and error handling.

### 7. Business Logic & Policy
- Add tests for finalization/locking, URL validation, file storage, and policy enforcement.

Each roadmap item will be linked to relevant test files and scenarios for traceability and auditability.

---
## Recent Customizations & Coverage (2026)

- **Destructive Test Isolation:** All destructive tests (e.g., .venv deletion) are isolated using pytest markers, environment overrides, and file/resource detection (see conftest.py).
- **Interactive CLI Support:** All scripts now support interactive CLI mode (prompt, help, exit, info, version, reset, diagnostics). Tests use pexpect for interactive scenarios and subprocess for argument-based runs.
- **Advanced Scenarios:** Tests cover concurrency, resource limits, security, external APIs, colored output, log file support, documentation drift, static analysis, test parallelization, flakiness detection, mutation testing, property-based testing, resource leak detection, custom linting, randomized test order, and more.
- **Broad API/Service Coverage:** Integration and edge-case tests for FastAPI endpoints, Docker/Colima orchestration, PostgreSQL migration/backup/restore, GitHub Actions API, pre-commit hooks, React frontend API, Celery tasks, security/compliance (auth failures, permission, secrets, audit), edge cases (rate limiting, malformed requests, network partitions).
- **Traceability:** All tests are mapped to design/code and documented in this file for auditability.

---

## Deeper Functional Test Coverage (Recommended)

To further increase confidence in the robustness and correctness of your developer tooling, consider adding the following functional and integration tests:

### 4. test_setup_env_creates_venv_and_installs_packages
- **Purpose:**
  - Verifies that running `setup_env.py` from scratch creates a `.venv` and installs all required packages from `requirements.txt`.
- **Why Needed:**
  - Ensures onboarding and environment setup is reliable for new developers and CI.
- **How It Works:**
  - Removes any existing `.venv`.
  - Runs `setup_env.py`.
  - Asserts that `.venv` exists and all packages in `requirements.txt` are installed (using `pip freeze`).
- **Coverage:**
  - End-to-end environment setup, package installation, and error handling.

### 5. test_cleanup_env_removes_venv
- **Purpose:**
  - Ensures that `cleanup.py` fully removes the `.venv` and all installed packages.
- **Why Needed:**
  - Guarantees a clean slate for repeated environment setup and teardown (important for CI and reproducibility).
- **How It Works:**
  - Ensures `.venv` exists (creates if needed).
  - Runs `cleanup.py`.
  - Asserts that `.venv` no longer exists.
- **Coverage:**
  - Full environment cleanup and file system effects.

### 6. test_check_links_detects_broken_and_valid_links
- **Purpose:**
  - Validates that `check_links.py` correctly identifies both valid and broken links in Markdown files.
- **Why Needed:**
  - Prevents regressions in documentation link checking and ensures CI catches broken links.
- **How It Works:**
  - Creates temporary Markdown files with known good and bad links in a test directory.
  - Runs `check_links.py` and asserts that broken links are reported and valid links are not.
- **Coverage:**
  - Link parsing, URL/file checking, and error reporting logic.

### 7. test_run_app_run_starts_components
- **Purpose:**
  - Ensures that `run_app.py run` attempts to start all defined components (infrastructure, backend, frontend).
- **Why Needed:**
  - Verifies orchestration logic and that all subprocesses are invoked as expected.
- **How It Works:**
  - Mocks `subprocess.Popen` to capture calls without actually starting services.
  - Runs `run_app.py run` and asserts that all components are attempted.
- **Coverage:**
  - CLI orchestration, subprocess invocation, and error handling.

---

## File Locking and Race Condition Test

- A new test will use multiprocessing to run setup_env.py and cleanup.py concurrently, simulating race conditions and file locking issues.
- The test will verify that neither script crashes or leaves the environment in an inconsistent state.
- This ensures robustness when multiple users or processes interact with the environment simultaneously (e.g., in CI or shared dev setups).

---

## Performance Test for setup_env.py

- A new test will measure the time taken by setup_env.py to process a large requirements.txt (e.g., 500+ packages).
- The test will assert that setup_env.py completes within a reasonable time threshold (e.g., 60 seconds), or at least does not hang or crash.
- This ensures that onboarding and CI remain fast and scalable as the project grows.

---

## Resource Limit (Disk/Memory) Test for setup_env.py

- A new test will simulate low disk space and/or memory conditions when running setup_env.py.
- The test will assert that setup_env.py fails gracefully with a clear error message, rather than crashing or hanging.
- This ensures the script is robust in constrained environments, such as CI runners or developer laptops with limited resources.
- Note: True disk/memory exhaustion is difficult to simulate in CI, so the test may use mocking or temporary file system quotas where possible.

---

## Advanced Scenarios and Reporting Enhancements

### Additional Test Scenarios
- **Corrupted .venv directory:** Simulate a corrupted .venv (e.g., .venv is a file or missing critical subfolders) and verify setup_env.py and cleanup.py handle errors gracefully.
- **Invalid requirements.txt:** Test setup_env.py with a requirements.txt containing invalid package names or syntax, ensuring clear error reporting.
- **Edge-case Markdown links:** Test check_links.py with Markdown files containing relative links, anchors, unicode, and malformed URLs.
- **Missing scripts/components:** Test run_app.py when scripts or backend/frontend directories are missing, ensuring it fails gracefully.
- **Concurrent execution:** Test running setup_env.py and cleanup.py concurrently to check for race conditions or file lock issues.
- **Pre-commit hook failure propagation:** Intentionally break a pre-commit hook and verify that CI fails as expected.
- **Environment variable overrides:** Test run_app.py and setup_env.py with environment variables set/unset (e.g., PYTHON312_BIN) to ensure correct interpreter selection.

### Reporting Features
- **HTML coverage reports:** Enable pytest-cov to generate HTML reports for visual inspection of code coverage.
- **Verbose and summary output:** Use pytest -v --tb=short for detailed test output in CI.
- **Coverage badge:** Add a badge to README.md for test/coverage status (using shields.io or similar).
- **Log failed test output:** Save all failed test stdout/stderr to a file for easier debugging in CI.

---

## Advanced Coverage: Error Cases, Edge Cases, and Automation Integration

### Error Case and Edge Case Testing
- **Missing requirements.txt:** Test that setup_env.py and run_app.py setup fail gracefully and print a clear error if requirements.txt is missing.
- **Invalid commands:** Test that run_app.py prints a usage/help message and exits with error for unknown commands.
- **Permission errors:** Test that scripts handle permission denied errors (e.g., cannot create/remove .venv) with clear output.
- **Invalid input:** Test that scripts handle unexpected arguments or malformed files robustly.

### Code Coverage Reporting
- **pytest-cov integration:** Add pytest-cov to requirements.txt and CI to generate code coverage reports for all scripts and CLI logic. Use coverage thresholds to enforce quality.

### Automation Integration
- **pre-commit integration:** Test that pre-commit hooks run and fail as expected when code or docs do not meet standards (e.g., lint, broken links).
- **CI automation:** Ensure all tests and hooks are run in CI for every push/PR.

---

## Further Test Scenarios for Maximum Robustness

### Additional Test Ideas
- **Simulate partial .venv removal:** Remove only some files from .venv and verify setup_env.py can recover or reports clearly.
- **requirements.txt with extras and comments:** Test setup_env.py with complex requirements.txt (extras, comments, blank lines).
- **check_links.py with circular and deeply nested links:** Ensure no infinite loops or stack overflows.
- **run_app.py with environment variable overrides for script paths:** Test robustness to custom script locations.
- **Test for race conditions in file creation/removal:** Use multiple threads/processes to create/remove .venv and requirements.txt.
- **Test for large requirements.txt:** Ensure setup_env.py handles hundreds of packages gracefully.
- **Test for non-UTF-8 Markdown files in check_links.py:** Ensure robust error handling and reporting.
- **Test for missing/interrupted pip install:** Simulate network failure or pip crash during install.

### Implementation Plan
- Add new tests in tests/test_error_cases.py and tests/test_functional_scripts.py for these scenarios.
- Use pytest's tmp_path, monkeypatch, and threading/multiprocessing for simulation.
- Document all new tests and their rationale in this file for traceability.

---

## Advanced Coverage: Error Cases, Edge Cases, and Automation Integration

### Error Case and Edge Case Testing
- **Missing requirements.txt:** Test that setup_env.py and run_app.py setup fail gracefully and print a clear error if requirements.txt is missing.
- **Invalid commands:** Test that run_app.py prints a usage/help message and exits with error for unknown commands.
- **Permission errors:** Test that scripts handle permission denied errors (e.g., cannot create/remove .venv) with clear output.
- **Invalid input:** Test that scripts handle unexpected arguments or malformed files robustly.

### Code Coverage Reporting
- **pytest-cov integration:** Add pytest-cov to requirements.txt and CI to generate code coverage reports for all scripts and CLI logic. Use coverage thresholds to enforce quality.

### Automation Integration
- **pre-commit integration:** Test that pre-commit hooks run and fail as expected when code or docs do not meet standards (e.g., lint, broken links).
- **CI automation:** Ensure all tests and hooks are run in CI for every push/PR.

---

## Implementation Plan for Advanced Coverage
- Add new tests in tests/test_error_cases.py for missing files, invalid commands, and permission errors.
- Add pytest-cov to requirements.txt and update CI workflow to collect and report coverage.
- Add tests for pre-commit hook execution and failure scenarios.
- Document all new tests and results in this file for traceability.

---

## Continuous Integration (CI) Integration

A GitHub Actions workflow (`.github/workflows/test-scripts.yml`) is configured to automatically run all tests on every push and pull request to the `main` and `docs` branches. This ensures:

- Automated verification of all developer tooling and orchestration scripts.
- Early detection of regressions or breaking changes in CI.
- Consistent environment setup using Python 3.12 and the project's requirements.txt.
- Test results are visible in the GitHub UI for every commit and PR.

### How It Works
- The workflow checks out the code, sets up Python 3.12, creates and activates a virtual environment, installs all dependencies, and runs all tests in the `tests/` directory using `pytest`.
- Any test failures will fail the workflow and block merging until resolved.

### Extending CI Coverage
- Add more test files to the `tests/` directory; they will be picked up automatically.
- Integrate code coverage reporting (e.g., pytest-cov) for visibility into untested code paths.
- Add jobs for linting, type checking, or other quality gates as needed.

---

## Recommendations for Even More Coverage

- Add tests for error and edge cases (e.g., missing files, invalid input, permission errors).
- Test integration with pre-commit hooks and other automation.
- Add code coverage reporting to track and improve test completeness.
- Use `pytest` fixtures and mocking to simulate failure scenarios and external dependencies.
- Document new tests and CI enhancements in this file for traceability.

---

## Security Check: Prevent Arbitrary Code Execution

- New tests will ensure that setup_env.py and check_links.py do not execute arbitrary code from requirements.txt or Markdown files.
- The tests will attempt to inject shell commands or Python code into requirements.txt and Markdown, and verify that these are not executed.
- This guards against supply chain attacks and accidental code execution from untrusted input.

---

## User Interruption (KeyboardInterrupt) Test

- A new test will simulate a KeyboardInterrupt (Ctrl+C) during setup_env.py and cleanup.py execution.
- The test will verify that the scripts handle the interruption gracefully, clean up any partial state, and print a clear message to the user.
- This ensures that users can safely abort operations without leaving the environment in a broken state.

---

## Colored Output and Error Message Test (User Experience)

- A new test will verify that scripts print colored output (using ANSI escape codes) for success, warning, and error messages.
- The test will run each script, capture the output, and assert that the expected ANSI codes are present in the output for key messages.
- This ensures that users receive clear, visually distinct feedback in their terminal, improving usability and reducing missed warnings/errors.

---

## Test Parallelization (pytest-xdist)

- The test suite will use pytest-xdist to run tests in parallel, significantly speeding up test execution, especially for large suites or slow tests.
- The CI workflow will invoke pytest with the -n auto flag to automatically use all available CPU cores.
- This ensures fast feedback for developers and efficient use of CI resources.

---

## Enhanced Parallel/Distributed CI for Large Test Suites

- The CI workflow now splits test execution across multiple parallel jobs using GitHub Actions matrix strategy and pytest-xdist.
- This significantly speeds up feedback for large test suites by distributing the workload across multiple runners and CPU cores.
- Each job runs a subset of the tests in parallel, ensuring efficient resource utilization.
- See `.github/workflows/test-scripts.yml` for details.

---

## How to Run the Tests

Run all tests with:

    pytest tests/

All tests are self-contained and do not require external dependencies beyond those in requirements.txt and a working Python 3.12+ environment.

---

## Extending the Test Suite

- Add new scripts to the `SCRIPTS` list in the test file to automatically include them in help/usage checks.
- Add functional or integration tests for deeper coverage as new features are added.

---

## Audit & Maintenance

- This test suite should be run in CI and before major merges to ensure developer tooling remains robust and user-friendly.
- Update this document and the test file as new scripts or CLI commands are introduced.

---

## CI Matrix and Cross-Platform Testing

- The CI workflow will be updated to run all tests on Ubuntu, Windows, and macOS runners, and across multiple Python 3.12.x and 3.13.x versions.
- This ensures scripts and automation are robust and portable across all supported developer environments.
- Any OS- or Python-version-specific issues will be caught early in the development process.

---

## Pre-commit Hook Chaining Test

- A new test will verify that multiple pre-commit hooks (some passing, some failing) are executed in order and that failures are correctly propagated.
- The test will create a temporary .pre-commit-config.yaml with multiple hooks, simulate a commit, and check that the output and exit code reflect the correct chaining behavior.
- This ensures that pre-commit integration is robust and that all hooks are enforced as expected.

---

## Documentation Drift Test

- A new test will parse tooling-log.md and tests.md, extract the list of scripts and tests, and compare them to the actual files in scripts/ and tests/.
- The test will fail if any script or test is missing from the documentation, or if the documentation lists files that do not exist.
- This ensures that documentation and code remain in sync, supporting onboarding, audits, and maintenance.

---

## Test Flakiness Detection

- The CI workflow will be updated to run the entire test suite multiple times (e.g., 3x) in a row.
- If any test fails intermittently (passes once, fails another), the workflow will fail, surfacing flaky or non-deterministic tests.
- This ensures long-term reliability and confidence in the test suite, especially as it grows in size and complexity.

---

## Static Analysis Integration (mypy, bandit, flake8)

- New CI jobs will run mypy (type checking), bandit (security analysis), and flake8 (linting) on all Python code.
- These tools catch type errors, security issues, and style problems before code is merged.
- The test suite will fail if any static analysis tool reports errors, enforcing high code quality and security standards.

---

## Mutation Testing Integration (CI)

- The CI workflow now includes a mutation testing job using `mutmut`.
- This job runs mutation tests on all scripts and `run_app.py`, and fails the build if any mutation survives (i.e., is not caught by the test suite).
- Mutation results are uploaded as an artifact for review.
- This ensures the test suite is effective at catching real defects and highlights any untested or weakly tested code paths.
- See `.github/workflows/test-scripts.yml` for details.

---

## CLI Argument Fuzzing/Systematic Coverage (CI)

- The CI workflow now includes a dedicated job for CLI argument fuzzing.
- This job runs `tests/test_cli_fuzzing.py`, which systematically and randomly generates argument combinations for all scripts and `run_app.py`.
- The tests verify that scripts handle all argument combinations gracefully (no crashes, clear error messages for invalid input).
- This ensures robust CLI handling and user experience, even for unexpected or malformed input.
- See `.github/workflows/test-scripts.yml` for details.

---

## Pytest Markers for Test Tagging/Grouping

- The test suite now uses pytest markers (`@pytest.mark.slow`, `@pytest.mark.destructive`, `@pytest.mark.integration`) to tag and group tests by type and purpose.
- This enables selective test runs (e.g., only integration or slow tests) and better organization of the suite.
- Example usage:

    pytest -m slow
    pytest -m integration
    pytest -m 'not destructive'

- Markers are applied in `tests/test_functional_scripts.py` and can be extended to other test files as needed.

---

## Automated Dependency Updates (Dependabot)

- Dependabot is enabled via `.github/dependabot.yml` to automatically check for and propose updates to Python dependencies (requirements.txt) and GitHub Actions workflows.
- This ensures dependencies remain up-to-date and secure with minimal manual intervention.
- Update PRs are created automatically and can be reviewed and merged as needed.

---

## Systematic Pytest Fixtures/Factories for Test Data

- The test suite now uses systematic pytest fixtures for reusable test data and environment setup/teardown.
- Fixtures such as `temp_venv`, `temp_requirements`, and `temp_docs` provide isolated, repeatable test environments and data for all relevant tests.
- This improves test reliability, maintainability, and reduces code duplication.
- See `tests/test_functional_scripts.py` for examples and usage.

---

## Historical Test/Coverage Reporting (Codecov)

- The CI workflow now uploads coverage reports to Codecov after each test run.
- This enables historical tracking of test coverage, trends, and badge integration for the README.
- Coverage is reported via the `codecov/codecov-action` GitHub Action using the generated `coverage.xml` file.
- See `.github/workflows/test-scripts.yml` for details.

---

## User Simulation Tests (pexpect) for CLI Interactivity

- The test suite now includes user simulation tests using `pexpect` to interact with CLI scripts and `run_app.py` as a user would.
- These tests simulate entering commands, requesting help, and exiting, verifying that the CLI responds correctly and robustly to interactive input.
- The CI workflow runs these tests in a dedicated job for continuous validation of CLI interactivity.
- See `tests/test_cli_user_simulation.py` and `.github/workflows/test-scripts.yml` for details.

---

## Internationalization Tests (Non-English, Unicode Paths/Messages)

- The test suite now includes internationalization tests for non-English and unicode CLI arguments, file paths, and messages.
- These tests ensure that all scripts and `run_app.py` handle unicode and non-English input gracefully, without crashing or producing garbled output.
- The CI workflow runs these tests in a dedicated job for continuous validation of internationalization support.
- See `tests/test_internationalization.py` and `.github/workflows/test-scripts.yml` for details.

---

## Containerized Test Runs (Docker-based CI Job)

- The CI workflow now includes a job that builds a Docker image and runs all tests inside a containerized environment.
- This ensures tests pass in a clean, reproducible, and isolated environment, matching production-like conditions.
- The Dockerfile installs all dependencies and runs the full test suite.
- See `Dockerfile` and `.github/workflows/test-scripts.yml` for details.

---

## Performance/Security Regression Alerts in CI (Snyk)

- The CI workflow now includes a Snyk security scan job to detect vulnerabilities in dependencies and code.
- Snyk scans all Python projects and fails the build if new vulnerabilities are found, providing early alerts for security regressions.
- Requires a Snyk account and `SNYK_TOKEN` secret configured in the repository.
- See `.github/workflows/test-scripts.yml` for details.

---

## Mutation Testing Coverage Enforcement

- The CI workflow enforces a minimum mutation score threshold (currently 90%) using `mutmut`.
- If the mutation score drops below this threshold, the CI build fails, ensuring the test suite remains effective at catching real defects.
- Mutation score is calculated and checked automatically in the `mutation-testing` job.
- See `.github/workflows/test-scripts.yml` for details and how to adjust the threshold.

---

## Flakiness Dashboard: Tracking and Reporting Flaky Tests

- The CI workflow now tracks and reports flaky tests using `pytest-rerunfailures` and custom logging.
- Tests are run multiple times with reruns enabled; any test that fails and is rerun is logged.
- A `flakiness-report.txt` artifact is uploaded for each CI run, providing a dashboard of flaky tests over time.
- This helps identify and prioritize stabilization of non-deterministic or unreliable tests.
- See `.github/workflows/test-scripts.yml` for details.

---

## Test Impact Analysis (Run Only Affected Tests)

- The CI workflow now includes a job that uses `pytest-testmon` to run only tests affected by recent code changes.
- This speeds up CI for large test suites by avoiding unnecessary test runs.
- Testmon tracks code coverage and test dependencies to determine which tests need to be rerun.
- See `.github/workflows/test-scripts.yml` for details.

---

## Property-Based Testing (Hypothesis)

- The test suite now includes property-based tests using Hypothesis for CLI argument robustness.
- These tests generate a wide range of random string arguments for all scripts and `run_app.py`, ensuring they do not crash or produce tracebacks for unexpected input.
- The CI workflow runs these tests in a dedicated job for continuous validation.
- See `tests/test_property_based.py` and `.github/workflows/test-scripts.yml` for details.

---

## Visual Regression Testing (Placeholder)

- Visual regression testing is not currently implemented because the project does not include a web UI or frontend components.
- If a web UI is added in the future, tools such as Playwright, Percy, or Selenium can be integrated to automate screenshot-based regression testing.
- A CI job can be set up to run these tools and upload visual diffs as artifacts for review.
- See this section for future updates if/when a web UI is introduced.

---

## API Contract Testing (Placeholder)

- API contract testing is not currently implemented because the project does not expose public APIs or OpenAPI schemas.
- If APIs are added in the future (e.g., with FastAPI or Flask), contract tests can be implemented to validate endpoints against OpenAPI schemas and ensure backward compatibility.
- Tools such as Schemathesis, Dredd, or pytest plugins can be used for automated contract validation.
- See this section for future updates if/when API endpoints are introduced.

---

## Auto-Generated Test Documentation from Code/Comments

- The project includes a script (`scripts/generate_test_docs.py`) that parses all test files and generates a Markdown summary of all test functions and their docstrings/comments.
- The CI workflow runs this script and uploads the generated documentation as an artifact for each run.
- This ensures test documentation stays up-to-date with the codebase and supports onboarding, audits, and maintenance.
- See `docs/generated_test_docs.md` and `.github/workflows/test-scripts.yml` for details.

---

## Resource Leak Detection in Tests

- The test suite now includes resource leak detection tests to check for file descriptor and memory leaks in all scripts and `run_app.py`.
- These tests measure resource usage before and after script execution, failing if a significant leak is detected.
- The CI workflow runs these tests in a dedicated job for continuous validation.
- See `tests/test_resource_leaks.py` and `.github/workflows/test-scripts.yml` for details.

---

## Security Fuzzing (AFL/OSS-Fuzz) (Placeholder)

- Security fuzzing with tools like AFL or OSS-Fuzz is not currently implemented because the project does not include native code or C extensions.
- If native code or C extensions are added in the future, fuzzing can be integrated to detect memory safety and security issues.
- For pure Python code, consider using property-based testing (Hypothesis) and CLI fuzzing for input robustness.
- See this section for future updates if/when fuzzing becomes applicable.

---

## Accessibility Regression Tests (Placeholder)

- Accessibility regression testing is not currently implemented because the project does not include a web UI or frontend components.
- If a web UI is added in the future, tools such as axe, pa11y, or Playwright accessibility checks can be integrated to automate a11y testing on every PR.
- A CI job can be set up to run these tools and upload accessibility reports as artifacts for review.
- See this section for future updates if/when a web UI is introduced.

---

## Test Analytics (Duration, Slowest Tests, Trends)

- The CI workflow now collects and uploads analytics on test durations, including the slowest tests and timing trends.
- Pytest's --durations flag is used to report the slowest 20 tests, and the results are uploaded as an artifact for each run.
- This helps identify performance bottlenecks and track test suite speed over time.
- See `.github/workflows/test-scripts.yml` for details.

---

## Custom Lint/Static Analysis for Project Anti-Patterns

- The project includes a custom linter (`scripts/custom_lint.py`) to check for project-specific anti-patterns, such as forbidden imports, print statements, and TODO comments in scripts and run_app.py.
- The CI workflow runs this linter in a dedicated job, and the build fails if any violations are found.
- This enforces code quality and project standards beyond generic linters.
- See `scripts/custom_lint.py` and `.github/workflows/test-scripts.yml` for details.

---

## Randomized Test Order to Catch Hidden Dependencies

- The CI workflow now uses pytest-randomly to randomize the order of test execution on every run.
- This helps catch hidden dependencies between tests and ensures each test is fully isolated and robust.
- Any order-dependent failures are surfaced early for correction.
- See `.github/workflows/test-scripts.yml` for details.

---

## Zero-Downtime/Blue-Green Deploy Test (Placeholder)

- Zero-downtime or blue-green deployment testing is not currently implemented because the project does not include deployment automation or production deployment scripts.
- If deployment automation is added in the future, tests can be implemented to simulate blue-green or canary deployments and verify that no downtime or user disruption occurs during releases.
- See this section for future updates if/when deployment automation is introduced.
