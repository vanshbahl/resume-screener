# Phase 3.1: Resume Profile Management Domain

## Overview
Phase 3.1 introduces the core Resume Profile Management domain. In the AI Resume Intelligence Platform, this domain serves as the primary user profile, transitioning the platform beyond a stateless intelligence engine into a robust application.

Instead of treating parsed Resumes as isolated files, we introduce a persistent `Candidate` (User Profile) model that natively integrates with our deterministic intelligence, search, and decision components.

## 1. Domain Architecture

The Resume Profile Management domain is fully isolated inside `app/candidate/` following Domain-Driven Design (DDD) principles:
```text
app/candidate/
├── api/             # HTTP endpoints and routing
├── events/          # Domain events (syncing with intelligence layer)
├── models/          # SQLAlchemy schemas (Candidate, Resume, Timeline, Notes)
├── repositories/    # Database abstraction layer
├── schemas/         # Pydantic Request/Response models
└── services/        # Business logic orchestration
```

## 2. The Candidate (User Profile) Entity

The `Candidate` model represents the User's core profile. 
A profile has:
- `id`: A unique String UUID.
- `status`: Driven by `statuses.yaml`.
- `tags`: A JSONB array driven by `tags.yaml`.
- `custom_fields`: A JSONB dictionary for dynamic metadata (e.g., `linkedin_url`, `expected_salary`).

### Resume Management
Users can upload multiple resumes. These are tracked in the `candidate_resumes` table. Only one resume is active at a time (`is_active = True`). When a new resume is uploaded, older resumes are deactivated, preserving historical context.

## 3. Timeline Engine

Every meaningful action is tracked immutably in the `candidate_timeline` table.
Actions tracked include:
- `candidate_created`
- `status_changed`
- `resume_uploaded`
- `resume_parsed`
- `note_added`

## 4. Automatic Intelligence Sync

Manual indexing is error-prone. The `app/candidate/events/sync.py` module automatically keeps the Profile aligned with the Intelligence Core:
1. When a resume finishes processing, the sync event fires.
2. It extracts `structured_data` and computes the `FeatureVector`.
3. It incorporates manual tags into the FeatureVector.
4. It indexes the profile into the high-performance in-memory Search Engine.

## 5. API Endpoints

All endpoints are exposed under `/candidates/`:
- `POST /candidates/`: Create a profile with initial fields.
- `GET /candidates/{id}`: Retrieve full profile details.
- `POST /candidates/{id}/status`: Update status.
- `POST /candidates/{id}/resume`: Upload and parse a new resume.
- `GET /candidates/{id}/timeline`: Retrieve the audit history.
- `POST /candidates/{id}/notes`: Add collaborative rich-text notes.

## Future Compatibility
By using a robust domain schema originally designed for ATS operations, the UI dashboards (Phase 4) can interact entirely with standard CRUD endpoints while the Intelligence core seamlessly works behind the scenes on `FeatureVector` updates.
