# Technical Requirements Document (TRD)

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |
| 2026-07-23 | 2.5     | Updated TRD for Phase 3 Backend Completion |

## 1. Architecture Overview
The platform utilizes a monolithic, domain-driven architecture. The FastAPI application serves REST endpoints organized by strict business boundaries (Candidate, Job, Workflow, Workspace, Interview, Analytics). Operations are strongly decoupled, utilizing Timeline Event logs to synchronize distributed state changes, while relying on `MemoryCacheRepository` to speed up analytical read operations.

## 2. Technology Stack
- **Frontend (Planned)**: React, TypeScript, Vite, TailwindCSS, shadcn/ui.
- **Backend API**: FastAPI, Pydantic, SQLAlchemy, Alembic, PyYAML.
- **Database & CI/CD**: PostgreSQL (with JSONB), `pgvector`, Pytest, GitHub Actions.
- **Text Extraction**: `PyMuPDF`, `PaddleOCR`.
- **NLP / ML**: `spaCy` (`en_core_web_trf`), HuggingFace NER (`dslim/bert-base-NER`), `sentence-transformers` (`BAAI/bge-small-en-v1.5`), `RapidFuzz`.

## 3. System Components
- **API Routers**: Organized per domain (e.g., `app/candidate/api/router.py`).
- **Pipeline Service**: Orchestrates text extraction and NLP via an Object-Oriented Pipeline (`BaseParserStage`).
- **Intelligence Engine**: Evaluates candidate metrics deterministically via Matching, Scoring, and Gap Analysis.
- **Core Domains**: 
  - `Job` and `Candidate` layers act as foundational models.
  - `Workflow Engine` orchestrates customizable hiring pipelines.
  - `Interview Management` handles scheduling, panels, and dynamic JSONB feedback scorecards.
  - `Workspace` provides caching and user-specific states.
  - `Analytics` aggregates data from all layers to calculate KPIs and build exportable CSV reports.
- **Data Layer**: Manages relational records, JSONB metadata, and vector embeddings via standard Repository patterns.

## 4. AI Components
- **Embedder**: `BAAI/bge-small-en-v1.5` (~130MB). Generates 384-dimensional dense vectors.
- **NLP Cleaner & Baseline NER**: `en_core_web_trf` (spaCy). Performs sentence boundary detection, normalization, and broad entity recognition.
- **Specialized NER**: `dslim/bert-base-NER` (HuggingFace). For high-precision extraction of ORG, PER, LOC.

## 5. Security
- **Data Isolation**: All AI models run locally; zero third-party API exposure.
- **Input Validation**: Strict typing enforced by Pydantic API boundaries.
- **Future Readiness**: The `user_id` context is already baked into Workspaces and Analytics, preparing the architecture for imminent Multi-Tenant RBAC implementations.

## 6. Performance
- **Caching**: Endpoints that hit heavy aggregations (`AnalyticsService`) are proxied through a globally injected `MemoryCacheRepository`.
- **Vectors**: `pgvector` executes exact K-NN cosine similarity directly within the database engine.
- **Background Tasks**: AI model loading and parsing are relegated off the main request thread to prevent UI lockups.

## 7. Scalability
- **MVP (Current)**: Vertical scaling. Bound by CPU limits on a single instance.
- **Data Architecture**: The database leverages extensive use of `JSONB` schemas (e.g. for scorecards and dashboard configs), permitting limitless template customization without causing database migration friction.

## 8. Deployment Strategy
- PostgreSQL is utilized in both Development and Testing (via testcontainers/docker-compose) to maintain feature parity (specifically for JSONB support).
- A GitHub Actions CI/CD pipeline validates every Pull Request using `Ruff`, `Black`, `isort`, `Mypy`, and `Pytest`.

## 9. Coding Standards
- PEP 8 for Python.
- Strict Domain-Driven Design (DDD). Services from one domain may invoke services of another, but they may not cross-pollinate database repositories directly.
- Clean Architecture (separation of API, Services, and Repositories).

## 10. Evaluation & Benchmarking
- **Testing Framework**: Complete 41-test suite encompassing full E2E scenarios across all domain implementations with 68% total coverage.
- **Parser Evaluation**: A custom benchmarking suite resides in `parser_tests/` capable of automated metric generation (Precision, Recall, F1) using a fuzzy-matching evaluation strategy on localized dataset generators.
