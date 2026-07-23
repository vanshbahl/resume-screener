# AI Document Intelligence Platform

A high-performance, offline-capable AI Resume Screening and Enterprise Applicant Tracking System (ATS) backend built for privacy and scale.

[![CI/CD Pipeline](https://github.com/vanshbahl/resume-screener/actions/workflows/ci.yml/badge.svg)](https://github.com/vanshbahl/resume-screener/actions/workflows/ci.yml)
![Coverage](https://img.shields.io/badge/coverage-68%25-brightgreen.svg)
![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

![Banner](docs/assets/banner.png)

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Current Status](#current-status)
- [Architecture Overview](#architecture-overview)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Screenshots](#screenshots)
- [Documentation](#documentation)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Future Plans](#future-plans)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Overview
The AI Document Intelligence Platform is designed to automate candidate evaluation and manage the entire hiring lifecycle. By utilizing offline open-source models, it securely parses documents and scores candidates without external LLM API costs or privacy risks. The robust backend provides comprehensive tools for job matching, interview scheduling, pipeline workflow management, and organizational analytics.

## Features
- **Offline AI Pipeline**: Entirely local extraction and NLP execution using `bge-small-en-v1.5`, `PaddleOCR`, and `spaCy`.
- **Intelligent Core**: Math-based candidate ranking, feature vectors, semantic similarity, and deterministic gap analysis.
- **Enterprise ATS Domains**: Independent modules for Job Management, Candidate Management, Workflow Pipelines, Interview Logistics, and Analytics.
- **Privacy First**: No data leaves your servers. No external LLM calls.
- **Generic Architecture**: Built with Domain-Driven Design (DDD) to effortlessly expand to multi-tenant scaling and additional document types.

## Current Status
**Phase 3 Complete (v2.5 Release Candidate 2)**: The platform has achieved complete stability across the core Applicant Tracking System. We have fully implemented Candidate Management, Job Management, configurable Pipeline Workflow Engines, the Recruiter Workspace, Interview Management (with JSONB Scorecards), and a comprehensive Analytics & Reporting Platform. The system is backed by a robust PostgreSQL testing infrastructure and automated CI/CD quality gates.

## Architecture Overview
The system relies on a monolithic FastAPI backend that processes AI tasks asynchronously while serving REST endpoints. A PostgreSQL database stores relational domain data alongside `JSONB` for unstructured extracted entities (resumes, scorecards, layouts) and `VECTOR` types for dense semantic embeddings. A strict Domain-Driven structure keeps the core modules decoupled.

## Tech Stack
- **Frontend (Planned)**: React, TypeScript, TailwindCSS, shadcn/ui, Vite
- **Backend API**: FastAPI, Pydantic, SQLAlchemy, Alembic, PyYAML
- **Database & Testing**: PostgreSQL with `pgvector`, Pytest, GitHub Actions
- **AI / NLP**: `spaCy`, `sentence-transformers`, `PaddleOCR`, `RapidFuzz`

## Folder Structure
```text
/
├── backend/
│   ├── app/
│   │   ├── intelligence/ # Matching, Scoring, Gap Analysis
│   │   ├── search/       # Candidate & Job Search Engine
│   │   ├── parsers/      # OOP Document Ingestion Pipeline
│   │   ├── candidate/    # Candidate Domain
│   │   ├── job/          # Job Domain
│   │   ├── workflow/     # Configurable Hiring Pipelines & Timelines
│   │   ├── interview/    # Scheduling, Panels, & Scorecards
│   │   ├── workspace/    # Recruiter Dashboards & Queues
│   │   ├── analytics/    # Aggregations, KPIs, CSV Reports
│   │   ├── models/       # Shared SQLAlchemy Base
│   │   └── main.py       # FastAPI Entrypoint
│   ├── config/           # YAML Rules & Configs
│   └── parser_tests/     # Comprehensive PyTest Integration & Benchmarking Suite
├── docs/                 # Project Documentation
├── docker-compose.yml    # Database Deployment
└── README.md
```

## Screenshots
*(Frontend Implementation Pending Phase 5)*

## Documentation
- [01_PRD.md](docs/01_PRD.md) - Product Requirements
- [02_TRD.md](docs/02_TRD.md) - Technical Requirements
- [03_UI_UX_DESIGN.md](docs/03_UI_UX_DESIGN.md) - Design System
- [04_APP_FLOW.md](docs/04_APP_FLOW.md) - Application Flow & Mermaid Diagrams
- [05_BACKEND_SCHEMA.md](docs/05_BACKEND_SCHEMA.md) - DB & Pipeline Architecture
- [06_IMPLEMENTATION_PLAN.md](docs/06_IMPLEMENTATION_PLAN.md) - Project Roadmap

## Getting Started

### Prerequisites
- Docker (for PostgreSQL + pgvector)
- Python 3.11+

### Local Setup
1. Start the database: `docker compose up -d`
2. Run Backend: `cd backend && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
3. Run Tests: `cd backend && PYTHONPATH=. pytest parser_tests/`

## Git Configuration
This repository strictly tracks source code, documentation, and configuration files.

To prevent repository bloat and accidental data leaks, our `.gitignore` explicitly filters:
- **Virtual Environments & Node Modules**: Language-specific local dependencies should never be committed.
- **Environment Variables (`.env`)**: Secrets and API keys must remain local to your machine.
- **Hugging Face Caches & Model Weights**: AI models are large binaries that are downloaded dynamically at runtime and should not reside in Git.
- **Uploads & Temporary Files**: Any user-uploaded resumes (`uploads/`) or temporary OS files (`.DS_Store`) are discarded.
- **Generated Datasets**: The testing folders generating mock PDFs are ignored to prevent bloat. Only the framework code is committed.

## Roadmap
See [06_IMPLEMENTATION_PLAN.md](docs/06_IMPLEMENTATION_PLAN.md) for detailed milestone tracking.

## Future Plans
- Organizations & RBAC (Multi-Tenancy).
- Full React Frontend Dashboard implementation.
- Distributed Celery/Redis worker node architecture.

## Contributing
Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
Maintained by Vansh Bahl
