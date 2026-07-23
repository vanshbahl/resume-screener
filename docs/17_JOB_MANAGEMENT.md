# Phase 3.2: Job Management Domain

## Overview
Phase 3.2 introduces the Job Management domain, acting as the second major pillar of the ATS. Jobs are no longer just simple rows attached to parsed JDs; they are rich, persistent business entities that support lifecycles, hiring teams, auditing, and seamless integration with the Intelligence Engine.

## 1. Domain Architecture

The Job Management domain is strictly isolated inside `app/job/` following Domain-Driven Design (DDD):
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

The new `Job` model replaces the legacy model and features:
- `id`: A unique String UUID.
- `status`: Configurable via `statuses.yaml` (e.g., `draft`, `open`, `closed`).
- `hiring_team`: A JSONB field defining roles like HM, recruiters, and interviewers.
- `tags`: A dynamic list of tags backed by `tags.yaml`.
- `custom_fields`: Org-specific metadata defined in `custom_fields.yaml` (e.g., `budget_code`).

### Job Descriptions
Jobs track historical `JobDescription` uploads. When a new JD is uploaded, older versions are deactivated, ensuring there is only one active JD per job at any time.

## 3. Timeline Engine

Every meaningful ATS action is tracked immutably in the `job_timeline` table.
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

Instead of manually synchronizing with the Intelligence Engine, the Job domain uses `app/job/events/sync.py`:
1. When a Job Description finishes parsing or when a Job's tags change, the sync event triggers.
2. It extracts `structured_data`, builds the `FeatureVector`, and pulls in manual Job Tags.
3. It pushes this directly to the `SearchService` (via `index_manager`).

This ensures that whenever a recruiter modifies a Job, the matching/search system instantly reflects those changes without external CRON jobs.

## 5. API Endpoints

The old Phase 1 `/jobs/` endpoints have been removed. The new structured API is exposed via `app/job/api/router.py`:
- `POST /jobs/`: Create a new Job requisition.
- `GET /jobs/`, `GET /jobs/{id}`: List and retrieve jobs.
- `PATCH /jobs/{id}`: Update core job metadata.
- `POST /jobs/{id}/status`: Transition a job to a new status (e.g., `open`).
- `POST /jobs/{id}/tags`: Assign operational tags.
- `POST /jobs/{id}/hiring-team`: Update assigned recruiters or managers.
- `POST /jobs/{id}/description`: Upload a PDF Job Description for parsing.
- `GET /jobs/{id}/timeline`: Retrieve the audit history.
- `POST /jobs/{id}/notes`: Add collaborative notes.

## Future Compatibility
The Job domain is now fully prepared to support future integrations like the ATS Pipeline (Phase 3.3), where the `JobCandidateAssociation` table will track candidates moving through stages (Applied -> Interview -> Offered).
