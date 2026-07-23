# Implementation Plan & Progress

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Tracking MVP Progress         |

---

## ✅ Completed Milestones

### Milestone 1: Ingestion Foundation
- **Objective:** Establish the backend framework and document processing infrastructure.
- **Deliverables:**
  - FastAPI application structure.
  - PostgreSQL + pgvector database models (SQLAlchemy).
  - Pydantic schemas.
  - PyMuPDF and PaddleOCR fallback extraction logic.
  - Asynchronous background task routing.

### Milestone 2: AI Pipeline Integration
- **Objective:** Process text locally without third-party APIs.
- **Deliverables:**
  - `spaCy` text cleaning.
  - Hardcoded skills dictionary for `RapidFuzz` extraction.
  - Semantic vector generation via `BAAI/bge-small-en-v1.5`.
  - JSONB database integration.

### Milestone 3: Semantic Search & Scoring
- **Objective:** Evaluate candidates against job requirements.
- **Deliverables:**
  - Deterministic Python scoring algorithm.
  - 60% weight to hard skill fuzzy matches.
  - 40% weight to soft skill semantic vector matching.
  - `/rankings/` REST endpoint.

---

## 🟡 In Progress Milestones

### Milestone 4: Frontend Development
- **Objective:** Build a React application for recruiters to interface with the platform.
- **Current Status:** Scaffolding complete (Vite, React, TypeScript). TailwindCSS installation encountered a minor issue and requires resolution.
- **Deliverables:**
  - shadcn/ui component library integration.
  - Dashboard view for active Jobs.
  - Drag-and-drop resume upload portal.
  - Candidate ranking table with score breakdown.

---

## ⚪ Planned Milestones

### Milestone 5: Containerization & Deployment
- **Objective:** Prepare the application for production deployment.
- **Deliverables:**
  - Dockerfile for the FastAPI backend (including AI model weights).
  - Multi-stage Dockerfile for React frontend.
  - Nginx reverse proxy configuration.
  - Documentation on VPS deployment.

### Milestone 6: Version 2 Enhancements
- **Objective:** Scale the system to new document types.
- **Deliverables:**
  - Celery / Redis background workers for heavy concurrency.
  - GLiNER Zero-Shot NER for dynamic entity extraction (Invoices/Medical).
  - Polymorphic parsing architecture.
