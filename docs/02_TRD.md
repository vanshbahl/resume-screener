# Technical Requirements Document (TRD)

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |

## 1. Architecture Overview
The platform utilizes a monolithic, single-process architecture for the MVP (YAGNI principle). The FastAPI application serves REST endpoints and simultaneously processes AI tasks asynchronously using native `BackgroundTasks`.

## 2. Technology Stack
- **Frontend**: React, TypeScript, Vite, TailwindCSS, shadcn/ui.
- **Backend API**: FastAPI, Pydantic, SQLAlchemy.
- **Database**: PostgreSQL.
- **Vector Extension**: `pgvector`.
- **Text Extraction**: `PyMuPDF`, `PaddleOCR`.
- **NLP / ML**: `spaCy`, `sentence-transformers` (`BAAI/bge-small-en-v1.5`), `RapidFuzz`.

## 3. System Components
- **API Router**: Handles HTTP Request/Response lifecycles and input validation.
- **Pipeline Service**: Orchestrates text extraction, cleaning, and model inference.
- **Scoring Engine**: Evaluates candidate metrics deterministically.
- **Data Layer**: Manages relational records, JSONB metadata, and vector embeddings.

## 4. AI Components
- **Embedder**: `BAAI/bge-small-en-v1.5` (~130MB). Generates 384-dimensional dense vectors.
- **NLP Cleaner**: `en_core_web_sm` (spaCy). Performs sentence boundary detection and normalization.
- **OCR Engine**: `PaddleOCR` (English Light). Handles scanned documents where PyMuPDF fails.

## 5. Security
- **Data Isolation**: All models run locally; zero third-party API exposure.
- **Input Validation**: Strict typing enforced by Pydantic.
- **File Uploads**: Sanitized filenames and strict MIME type checking (PDFs only for MVP).

## 6. Performance
- AI models are loaded into memory once at application startup to prevent high latency during inference.
- `pgvector` executes exact K-NN cosine similarity directly within the database engine, avoiding large data transfers.

## 7. Scalability
- **MVP (Current)**: Vertical scaling. Bound by CPU limits on a single instance.
- **V2 (Planned)**: Abstract AI Pipeline into a Celery Worker Pool, allowing horizontal scaling of GPU/CPU nodes independent of the web server.

## 8. Deployment Strategy
- Dockerized PostgreSQL container for the database layer.
- Backend and Frontend can be deployed via Docker Compose or native PM2 / Systemd services on a standard Ubuntu VPS.

## 9. Coding Standards
- PEP 8 for Python.
- Prettier & ESLint for React/TypeScript.
- Clean Architecture (separation of API, Services, and Data layers).
