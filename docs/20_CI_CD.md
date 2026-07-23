# CI/CD Pipeline Infrastructure

The Recruitment Intelligence Platform uses GitHub Actions for continuous integration, security scanning, and deployment readiness verification. 

## Overview

The CI/CD pipeline ensures that no code reaches the `main` branch unless it passes rigorous automated checks. 

The pipeline is split into two primary workflows:
1. **CI/CD Pipeline (`ci.yml`)**: Runs on Pull Requests and pushes to `main`.
2. **Release Validation (`release.yml`)**: Runs on version tags (`v*`) to package artifacts and verify deployment stability.

---

## 1. Quality Gates

The `ci.yml` workflow enforces the following gates before any code is considered valid:

- **Formatting**: `black` ensures strict PEP-8 compliant formatting. `isort` organizes imports alphabetically and logically.
- **Linting**: `ruff` performs blazing-fast static analysis to catch syntax issues, undefined variables, and bad practices.
- **Typing**: `mypy` statically checks Python type hints to ensure architectural correctness.
- **Testing**: `pytest` executes unit, integration, and API tests.
- **Coverage**: `pytest-cov` generates HTML and XML coverage reports.
- **Database & Startup**: Alembic migrations and FastAPI boot process are explicitly validated to prevent fatal runtime crashes in production.

---

## 2. Security Checks

Security is built directly into the CI pipeline:
- **Bandit**: Analyzes the Python AST (Abstract Syntax Tree) to find common security vulnerabilities (e.g. hardcoded passwords, dangerous shell execution).
- **pip-audit**: Scans the Python environments (`requirements.txt` and `requirements-dev.txt`) for known vulnerabilities listed in the PyPA advisory database.
- **Trufflehog**: Detects leaked secrets, API keys, and sensitive tokens across all git commits in the PR.

---

## 3. Database & Ephemeral Testing

The automated tests are configured to use ephemeral instances of **PostgreSQL**.
During CI execution, `testcontainers` dynamically provisions a localized Postgres instance using Docker, runs the entire test suite (including migrations), and transparently destroys the container when finished. This ensures 100% parity with production environments without manual orchestration.

---

## 4. Debugging CI Failures

If a GitHub Action fails, follow these steps:

1. **Click the Failing Job**: Go to the "Actions" tab in GitHub and click the failing job (e.g., `Code Quality & Linting`).
2. **Review Logs**: Expand the step that failed. 
    - If `pytest` failed, search for `FAILURES` or `ERROR`.
    - If `mypy` failed, it will list the file and line number with the type conflict.
3. **Reproduce Locally**: Ensure you have installed development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```
   Then manually run the failing command, for example:
   ```bash
   black --check app/
   mypy app/
   pytest
   ```
4. **Artifacts**: For test failures, download the `coverage-report` or `test-results` artifacts at the bottom of the Action summary page to view detailed logs in your browser.

---

## 5. Adding New Checks

To add a new tool or check to the pipeline:
1. **Add Dependency**: Update `backend/requirements-dev.txt` with the new tool package.
2. **Update Workflow**: Edit `.github/workflows/ci.yml`. Add a new step under the appropriate job (e.g. `security` or `code-quality`).
3. **Configure Tool**: If the tool requires configuration, add it to `backend/pyproject.toml` or `backend/pytest.ini`.

*Note: The platform caches `pip` packages and Hugging Face models (`~/.cache/huggingface`). If you update large models or dependencies, the cache will automatically invalidate based on the hash of `requirements.txt`.*
