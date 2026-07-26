# Phase 3.2: Job Description Benchmarking Domain

## Overview
Phase 3.2 covers the Job Management domain. In the context of the Resume Intelligence Platform, this domain is categorized as a **Future Capability**. 
Originally built to track open requisitions for recruiters, it now serves as a robust foundation for a future feature: **Job Description Benchmarking**, where job seekers can compare their resumes against specific, active job descriptions.

## 1. Domain Architecture

The Job domain is strictly isolated inside `app/job/` following Domain-Driven Design (DDD):
```text
app/job/
├── api/             # REST API routes for /jobs/
├── events/          # Domain events (syncing with intelligence layer)
├── models/          # SQLAlchemy schemas (Job, JobDescription, Timeline, Notes)
├── repositories/    # SQLAlchemy data abstraction
├── schemas/         # Pydantic Request/Response models for validation
└── services/        # Orchestrated business logic
```

## 2. Core Job Entity

The `Job` model features:
- `id`: A unique String UUID.
- `status`: Configurable via `statuses.yaml` (e.g., `draft`, `open`, `closed`).
- `hiring_team`: A JSONB field.
- `tags`: A dynamic list of tags backed by `tags.yaml`.
- `custom_fields`: Specific metadata defined in `custom_fields.yaml`.

### Job Descriptions
Jobs track historical `JobDescription` uploads. When a new JD is uploaded, older versions are deactivated, ensuring there is only one active JD per job at any time.

## 3. Timeline Engine

Every meaningful action is tracked immutably in the `job_timeline` table.
Tracked events include:
- `job_created`
- `job_updated`
- `status_changed`
- `tags_updated`
- `hiring_team_updated`
- `jd_uploaded`
- `jd_parsed`
- `note_added`

## 4. Automatic Intelligence Sync

The Job domain uses `app/job/events/sync.py`:
1. When a Job Description finishes parsing or when a Job's tags change, the sync event triggers.
2. It extracts `structured_data`, builds the `FeatureVector`, and pulls in manual Job Tags.
3. It pushes this directly to the `SearchService` (via `index_manager`).

This ensures that whenever a JD is added or modified, the matching/search system instantly reflects those changes.

## 5. API Endpoints

The API is exposed via `app/job/api/router.py`:
- `POST /jobs/`: Create a new Job benchmark.
- `GET /jobs/`, `GET /jobs/{id}`: List and retrieve jobs.
- `PATCH /jobs/{id}`: Update core job metadata.
- `POST /jobs/{id}/status`: Transition a job to a new status.
- `POST /jobs/{id}/tags`: Assign operational tags.
- `POST /jobs/{id}/hiring-team`: Update assigned teams.
- `POST /jobs/{id}/description`: Upload a PDF Job Description for parsing.
- `GET /jobs/{id}/timeline`: Retrieve the audit history.
- `POST /jobs/{id}/notes`: Add collaborative notes.

## Future Capability Utilization
While this module is fully implemented in the backend, it will not be prominently featured in the Phase 4 B2C UI until the "Targeted JD Benchmarking" features are rolled out in a later phase.
