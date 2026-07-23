# Phase 3.3: Workflow Engine

## Overview
The Workflow Engine (Phase 3.3) orchestrates the hiring lifecycle. It connects Candidates and Jobs through configurable Pipelines. It supports transitions, approvals, stage assignments, and maintains an immutable timeline of events.

## 1. Architecture

The Workflow domain (`app/workflow/`) is built using Domain-Driven Design principles, entirely isolated from the inner workings of the Candidate and Job domains, interacting with them via Events.

```text
app/workflow/
├── api/             # REST endpoints (/workflows)
├── events/          # Domain events to push updates to Candidate/Job timelines
├── models/          # SQLAlchemy schemas (Pipeline, Workflow, Approvals, Timeline)
├── repositories/    # Database operations
├── schemas/         # Pydantic validation models
└── services/        # Business logic for transitions and approvals
```

## 2. Core Entities

1. **Pipeline**: A template or job-specific definition of hiring stages.
2. **PipelineStage**: An individual step (e.g., `Applied`, `Technical Interview`, `Offer`). Stages can require approval or be marked terminal (e.g., `Hired`).
3. **WorkflowInstance**: The union of a `Candidate` and a `Job`. Tracks the `current_stage_id` and overall `status` (`active`, `rejected`, `withdrawn`, `hired`).
4. **Approval**: A record of a decision made at a stage gate (e.g., Offer Approval).
5. **Assignment**: A record of the user responsible for a stage (e.g., assigning a Recruiter or Hiring Manager).
6. **WorkflowTimeline**: An immutable log of all actions taken against the workflow.

## 3. Configuration Driven

The Workflow Engine avoids hardcoded logic.
1. `config/workflow/pipeline_templates.yaml`: Defines default organizational pipelines (e.g., Standard Engineering, Executive).
2. `config/workflow/transition_rules.yaml`: Defines global constraints, such as `no_skip_approval` (prevents skipping an unapproved stage).

## 4. State Transitions

The core of the workflow engine is the `transition_workflow` service method. It supports:
- `forward`: Moving to the next stage. Validates against `transition_rules.yaml` (e.g., ensuring prior approvals were granted).
- `reject` / `withdraw`: Terminates the workflow instance.

## 5. Event Syncing (Search Integration)

Whenever a workflow transitions, an event is fired in `app/workflow/events/sync.py`.
This event:
1. Pushes a log to the `CandidateTimeline` so recruiters viewing the candidate see the workflow update.
2. Pushes a log to the `JobTimeline`.
3. (Designed for) Updating the underlying Search Engine feature vector, enabling complex UI filtering like "Show me all Candidates in the 'Offer' stage for Job X".

## Future Extensibility
Because the Pipeline is represented as a Database Model (seeded by YAML), future features can allow recruiters to dynamically insert new stages into a specific Job's pipeline directly from a UI, without changing code.
