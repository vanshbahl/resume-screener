# Phase 3.1: Candidate Management Domain

## Overview
Phase 3.1 introduces the core Candidate Management domain, transitioning the platform from a standalone intelligence engine into a production-grade Applicant Tracking System (ATS). 

Instead of treating parsed Resumes as the primary business entity, we introduce a persistent `Candidate` model that natively integrates with our deterministic intelligence, search, and decision components.

## 1. Domain Architecture

The Candidate Management domain is fully isolated inside `app/candidate/` following Domain-Driven Design (DDD) principles:
```text
app/candidate/
├── api/             # HTTP endpoints and routing
├── events/          # Domain events (syncing with intelligence layer)
├── models/          # SQLAlchemy schemas (Candidate, Resume, Timeline, Notes)
├── repositories/    # Database abstraction layer
├── schemas/         # Pydantic Request/Response models
└── services/        # Business logic orchestration
```

## 2. The Candidate Entity

The `Candidate` model replaces `Resume` as the root entity. 
A candidate has:
- `id`: A unique String UUID.
- `status`: Driven by `statuses.yaml` (e.g., `applied`, `screening`, `manager_interview`).
- `tags`: A JSONB array driven by `tags.yaml`.
- `custom_fields`: A JSONB dictionary for dynamic metadata (e.g., `linkedin_url`, `expected_salary`).

### Resume Management
Candidates can upload multiple resumes. These are tracked in the `candidate_resumes` table. Only one resume is active at a time (`is_active = True`). When a new resume is uploaded, older resumes are deactivated, preserving historical context.

## 3. Timeline Engine

Every meaningful ATS action is tracked immutably in the `candidate_timeline` table.
Actions tracked include:
- `candidate_created`
- `status_changed`
- `resume_uploaded`
- `resume_parsed`
- `note_added`

## 4. Automatic Intelligence Sync

Manual indexing is error-prone. The `app/candidate/events/sync.py` module automatically keeps the Candidate aligned with the Intelligence Core:
1. When a resume finishes processing, the sync event fires.
2. It extracts `structured_data` and computes the `FeatureVector`.
3. It incorporates manual Candidate tags into the FeatureVector.
4. It indexes the candidate into the high-performance in-memory Search Engine.

## 5. API Endpoints

All endpoints are exposed under `/candidates/`:
- `POST /candidates/`: Create a candidate with initial fields.
- `GET /candidates/{id}`: Retrieve full candidate details.
- `POST /candidates/{id}/status`: Update applicant status.
- `POST /candidates/{id}/resume`: Upload and parse a new resume.
- `GET /candidates/{id}/timeline`: Retrieve the audit history.
- `POST /candidates/{id}/notes`: Add collaborative rich-text notes.

## Future Compatibility
By using a robust Candidate Domain, future Phase 5 UI dashboards can interact entirely with standard CRUD endpoints while the Intelligence core seamlessly works behind the scenes on `FeatureVector` updates.
