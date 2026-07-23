# Test Infrastructure (Phase 1)

## Overview
This document outlines the production-grade test environment implemented for the Recruitment Intelligence Engine.

In order to ensure that automated tests accurately mirror the production environment (which relies heavily on PostgreSQL features like `JSONB`), the testing infrastructure strictly uses **PostgreSQL**. The previously used in-memory SQLite setup has been entirely deprecated to avoid schema compilation errors and behavioral discrepancies.

## Architecture

1. **Testcontainers (`testcontainers[postgres]`)**: 
   - We utilize Testcontainers to automatically spin up a fresh, ephemeral PostgreSQL Docker container when the test suite starts.
   - It is bound to the `pytest` session scope, meaning it starts once when you run `pytest` and tears down automatically when the tests complete. No manual `docker-compose up` is required.

2. **Transaction Rollbacks (`db_session` fixture)**:
   - To ensure fast, deterministic tests, the database schema is created only once per session.
   - For every individual test, the `db_session` fixture begins a database transaction and yields the session to the test.
   - After the test completes (pass or fail), the transaction is **rolled back**, completely erasing any mutations made during the test. This guarantees that test state does not bleed into subsequent tests.

3. **Factory Boy**:
   - Instead of writing verbose and repetitive database setup code for every test, we utilize `factory_boy`.
   - Factories are located in `backend/parser_tests/factories/` and provide a clean API for generating fake domain entities (Candidates, Jobs, Workflows) with randomized data using `Faker`.

4. **Coverage & Markers**:
   - `pytest.ini` is configured to track test coverage using `pytest-cov`, generating Terminal, HTML, and XML output for the `app` module.
   - Custom markers (`@pytest.mark.unit`, `@pytest.mark.integration`, etc.) are defined to allow selective test execution.

## Execution

### Run all tests
From the `backend/` directory:
```bash
# Be sure to set PYTHONPATH=. so the `app` module resolves correctly
PYTHONPATH=. venv/bin/pytest
```

### Run specific markers
```bash
PYTHONPATH=. venv/bin/pytest -m "integration"
```

### Coverage Reports
After running pytest, a terminal summary will be printed.
Additionally, you can view the HTML coverage report by opening:
```bash
open htmlcov/index.html
```

## Adding New Tests
1. **Always use the `client` fixture** for API tests. The `client` fixture is automatically injected with the isolated, rolling-back `db_session`.
   ```python
   def test_some_api(client):
       response = client.get("/some/endpoint")
       assert response.status_code == 200
   ```
2. **Use Factories** for database seeding.
   ```python
   from parser_tests.factories.candidate_factory import CandidateFactory
   
   def test_candidate_logic(db_session):
       candidate = CandidateFactory() # automatically committed to the test session
       assert candidate.id is not None
   ```
3. **Do NOT mock the database** unless testing external service failure states. The ephemeral Postgres container is fast enough to support real database operations for all integration tests.
