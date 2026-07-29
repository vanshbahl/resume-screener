# AI Resume Intelligence Platform

A high-performance, offline-capable AI Resume Intelligence Platform built for privacy and scale. It helps students and job seekers understand how competitive their resume is compared to industry expectations and other users.

[![CI/CD Pipeline](https://github.com/vanshbahl/resume-screener/actions/workflows/ci.yml/badge.svg)](https://github.com/vanshbahl/resume-screener/actions/workflows/ci.yml)
![Coverage](https://img.shields.io/badge/coverage-68%25-brightgreen.svg)
![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

![Banner](docs/assets/banner.png)

## Table of Contents
- [Overview](#overview)
- [Primary Workflow](#primary-workflow)
- [Platform Architecture](#platform-architecture)
- [Current Status](#current-status)
- [Tech Stack](#tech-stack)
- [Folder Structure](#folder-structure)
- [Screenshots](#screenshots)
- [Documentation](#documentation)
- [Getting Started](#getting-started)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## Overview
The AI Resume Intelligence Platform is designed to empower job seekers by providing deep, actionable insights into their resumes. By utilizing offline open-source models, it securely parses documents, scores resumes, and offers personalized feedback without external LLM API costs or privacy risks. The robust backend intelligence engine powers everything from semantic benchmarking to AI-driven career recommendations.

## Primary Workflow
The platform is built around a streamlined user journey:
1. **User Uploads Resume**
2. **Resume is Parsed** (Offline PDF ingestion)
3. **System Extracts Structured Information**
4. **AI Follow-up** (Intelligently asks for missing information)
5. **Generate Resume Intelligence Report**
6. **Provide Overall Score**
7. **Show Industry Benchmark**
8. **Show Strengths & Weaknesses**
9. **Provide Actionable Recommendations**
10. **Rank Resume against the Platform's Dataset**

## Platform Architecture
Our strict Domain-Driven Design (DDD) separates the backend into clean, decoupled modules. Rather than forcing every backend module into the primary user flow, we categorize our architecture cleanly:

### 1. Current Product (Resume Intelligence)
These modules form the core of the AI Resume Intelligence Platform:
- **Resume Upload & Parsing**: The core pipeline for extracting PDF resumes (`app/parsers/`).
- **Resume Intelligence & Scoring**: The engine responsible for semantic extraction and gap analysis (`app/intelligence/`).
- **Resume Benchmarking & Ranking**: Utilizing the Vector database to rank resumes against the platform dataset (`app/search/`).
- **AI Feedback & Follow-ups**: Using local AI models to ask missing questions and provide personalized recommendations (`app/ai/`).
- **Resume Profile Management**: Unified tracking of applicant status, metadata, and resumes (`app/candidate/`).

### 2. Supporting Infrastructure
These modules run silently behind the scenes to power the platform:
- **Authentication & Identity**: User Accounts and stateless JWT authentication (`app/identity/`).
- **User Notifications**: Email and in-app alerts (`app/communication/`).
- **Platform Analytics**: Engagement and usage metrics (`app/analytics/`).
- **Search Engine**: The high-performance retrieval system.
- **User Workspace**: Managing user dashboard feeds (`app/workspace/`).

### 3. Future Capabilities
These modules are fully implemented in the backend (originally built as an ATS foundation), but are not the primary focus of the B2C Resume Intelligence platform today. They provide a robust foundation for future features:
- **Interview Platform**: Designed for scheduling, it can be repurposed later for Mock Interviews (`app/interview/`).
- **Internal Processing Pipeline**: Originally a workflow engine, this remains preserved for future internal tracking and career roadmaps (`app/workflow/`).
- **Organizations & Teams**: Included in the Identity module, providing a foundation for future B2B university cohorts or team collaboration.
- **Job Description Benchmarking Engine**: Originally built for recruiters, this forms the underlying schema for future JD benchmarking (`app/job/`).

## Current Status
**Phase 3 Complete (v2.5 Release Candidate 2)**: The platform has achieved complete stability across the core backend engine. The intelligence modules, supporting infrastructure, and future capability schemas are fully implemented, backed by a robust PostgreSQL testing infrastructure and automated CI/CD quality gates.

## Tech Stack
- **Frontend**: React, TypeScript, TailwindCSS, Framer Motion, Vite
- **Backend API**: FastAPI, Pydantic, SQLAlchemy, Alembic, PyYAML
- **Database & Testing**: PostgreSQL with `pgvector`, Pytest, GitHub Actions
- **AI / NLP**: `spaCy`, `sentence-transformers`, `PaddleOCR`, `RapidFuzz`

## Folder Structure
```text
/
├── backend/
│   ├── app/
│   │   ├── intelligence/    # Resume Scoring, Gap Analysis
│   │   ├── search/          # Resume Benchmarking & Ranking
│   │   ├── parsers/         # OOP Document Ingestion Pipeline
│   │   ├── candidate/       # Resume Profile Management
│   │   ├── job/             # Job Description Benchmarking
│   │   ├── workflow/        # Internal Processing Pipelines
│   │   ├── interview/       # Future Mock Interview Platform
│   │   ├── workspace/       # User Dashboard & Feeds
│   │   ├── analytics/       # Platform Engagement Analytics
│   │   ├── identity/        # User Accounts & Auth
│   │   ├── communication/   # User Notifications
│   │   ├── ai/              # AI Feedback, Copilot, Prompts
│   │   ├── models/          # Shared SQLAlchemy Base
│   │   └── main.py          # FastAPI Entrypoint
│   ├── config/           # YAML Rules & Configs
│   └── parser_tests/     # Comprehensive PyTest Integration Suite
├── frontend/             # React SPA (Vite, Tailwind, Framer Motion)
├── docs/                 # Project Documentation
├── docker-compose.yml    # Database Deployment
└── README.md
```

## Screenshots
*(Dashboard UI Pending Phase 4. Landing page implementation complete.)*

## Documentation
- [01_PRD.md](docs/01_PRD.md) - Product Requirements
- [02_TRD.md](docs/02_TRD.md) - Technical Requirements
- [03_UI_UX_DESIGN.md](docs/03_UI_UX_DESIGN.md) - Design System
- [04_APP_FLOW.md](docs/04_APP_FLOW.md) - Application Flow & Mermaid Diagrams
- [05_BACKEND_SCHEMA.md](docs/05_BACKEND_SCHEMA.md) - DB Architecture
- [06_IMPLEMENTATION_PLAN.md](docs/06_IMPLEMENTATION_PLAN.md) - Project Roadmap

## Getting Started

### Prerequisites
- Docker (for PostgreSQL + pgvector)
- Node.js & npm (for Frontend)
- Python 3.11+

### Local Setup
1. Start the database: `docker compose up -d`
2. Run Backend: `cd backend && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
3. Run Frontend: `cd frontend && npm install && npm run dev`
4. Run Tests: `cd backend && PYTHONPATH=. pytest parser_tests/`

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

- **Phase 4**: Resume Intelligence Frontend (Landing Page Complete, Dashboards Pending)
- **Phase 5**: Resume Intelligence (Backend Scoring Engine Complete, Insights & UI Pending)
- **Phase 6**: AI Enhancements (Resume Rewriting, Job-specific Optimization)

## Contributing
Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
Maintained by Vansh Bahl
