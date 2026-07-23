# AI Document Intelligence Platform

A high-performance, offline-capable AI Resume Screening and Document Processing engine built for privacy and scale.

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

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
The AI Document Intelligence Platform is designed to automate the arduous task of evaluating candidate profiles against job requirements without incurring the latency, cost, or privacy risks of third-party LLM APIs (like OpenAI or Claude). It leverages state-of-the-art open-source Hugging Face models running locally.

## Features
- **Offline AI Pipeline**: Entirely local execution using `bge-small-en-v1.5`, `PaddleOCR`, and `spaCy`.
- **Deterministic Scoring**: Transparent, math-based candidate ranking using fuzzy matching and vector cosine similarity.
- **Privacy First**: No data leaves your servers. No external LLM calls.
- **Generic Core**: Polymorphic architecture designed to scale beyond resumes to Invoices and POs.

## Current Status
**Phase 2 Complete**: We have finalized a Hybrid Information Extraction Engine leveraging spaCy and Hugging Face models (`dslim/bert-base-NER`) alongside domain-specific regex extractors. A robust programmatic testing environment has been established, including an automated parser evaluation framework, a regression guard, and a synthesizer that generated a 50-resume benchmark dataset.

## Architecture Overview
The system relies on a monolithic FastAPI backend that handles both web requests and async AI processing via `BackgroundTasks`. A PostgreSQL database stores relational data alongside `JSONB` for unstructured extracted entities and `VECTOR` types for dense semantic embeddings.

## Tech Stack
- **Frontend**: React, TypeScript, TailwindCSS, shadcn/ui, Vite
- **Backend**: FastAPI, Pydantic, SQLAlchemy, Alembic, PyYAML
- **Database**: PostgreSQL with `pgvector`
- **AI / NLP**: `spaCy`, `sentence-transformers`, `PaddleOCR`, `RapidFuzz`

## Folder Structure
```text
/
├── backend/
│   ├── app/parsers/     # Object-Oriented Document Pipeline
│   ├── config/          # PyYAML Rules & Regex Configs
│   ├── development/     # Sandbox tools, experiments, scratch scripts
│   └── parser_tests/    # Benchmarking Framework & Dataset Generator
├── frontend/            # React Web Client
├── docs/                # Project Documentation
├── docker-compose.yml   # Local Database Deployment
└── README.md
```

## Screenshots

![Dashboard](docs/assets/dashboard.png)
*Figure 1: Candidate Ranking Dashboard*

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
- Node.js 18+
- Python 3.11+

### Local Setup
1. Start the database: `docker compose up -d`
2. Run Backend: `cd backend && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
3. Run Frontend: `cd frontend && npm run dev`

## Git Configuration
This repository strictly tracks source code, documentation, and configuration files.

To prevent repository bloat and accidental data leaks, our `.gitignore` explicitly filters:
- **Virtual Environments & Node Modules**: Language-specific local dependencies should never be committed.
- **Environment Variables (`.env`)**: Secrets and API keys must remain local to your machine.
- **Hugging Face Caches & Model Weights**: AI models are large binaries that are downloaded dynamically at runtime and should not reside in Git.
- **Uploads & Temporary Files**: Any user-uploaded resumes (`uploads/`) or temporary OS files (`.DS_Store`) are discarded.
- **Generated Datasets**: The `parser_tests/datasets/` and `parser_tests/results/` folders (PDFs, JSONs, Benchmark Charts) are ignored. Only the testing *framework* code itself is committed.

## Roadmap
See [06_IMPLEMENTATION_PLAN.md](docs/06_IMPLEMENTATION_PLAN.md) for detailed milestone tracking.

## Future Plans
- Invoice and Purchase Order intelligent parsing.
- Transition to Celery/Redis for distributed worker nodes.
- HNSW indexing in pgvector for massive scale.

## Contributing
Contributions are welcome! Please read `CONTRIBUTING.md` for details on our code of conduct and the process for submitting pull requests.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Author
Maintained by Vansh Bahl

## Acknowledgements
## Git Configuration
This repository maintains a strict `.gitignore` policy to prevent sensitive or unnecessary files from being committed:
- **Virtual Environments & Node Modules**: (`venv/`, `node_modules/`) are ignored to keep the repository lightweight and OS-agnostic.
- **Environment Variables**: (`.env`) are ignored to prevent accidentally leaking API keys and database credentials.
- **Model Weights & Cache**: Hugging Face caches and localized model weights (`.cache/`, `hf_cache/`) are ignored due to extreme file sizes.
- **Uploaded Files**: Uploaded PDFs (`uploads/`) are ignored to protect PII and prevent repository bloat.

**Only source code, configuration files, and documentation should be committed.**
