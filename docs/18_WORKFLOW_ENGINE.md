# Phase 3.3: Internal Processing Pipeline

## Overview
Phase 3.3 covers the Workflow Engine. In the context of the Resume Intelligence Platform, this domain is categorized as a **Future Capability**. 
Originally built to orchestrate enterprise hiring lifecycles, this robust state machine is preserved as a foundation for tracking complex internal processing pipelines or future user career roadmaps.

## 1. Architecture

The Workflow domain (`app/workflow/`) is built using Domain-Driven Design principles, entirely isolated from the inner workings of the Candidate and Job domains, interacting with them via Events.

```text
app/workflow/
├── api/             # REST endpoints (/workflows)
├── events/          # Domain events to push updates to Timelines
├── models/          # SQLAlchemy schemas (Pipeline, Workflow, Approvals, Timeline)
├── repositories/    # Database operations
├── schemas/         # Pydantic validation models
└── services/        # Business logic for transitions and approvals
```

## 2. Core Entities

1. **Pipeline**: A template definition of processing stages.
2. **PipelineStage**: An individual step (e.g., `Applied`, `Technical Interview`, `Offer`). Stages can require approval or be marked terminal.
3. **WorkflowInstance**: The union of a `Candidate` (User) and a `Job` (Benchmark Target). Tracks the `current_stage_id` and overall `status`.
4. **Approval**: A record of a decision made at a stage gate.
5. **Assignment**: A record of the user responsible for a stage.
6. **WorkflowTimeline**: An immutable log of all actions taken against the workflow.

## 3. Configuration Driven

The Workflow Engine avoids hardcoded logic.
1. `config/workflow/pipeline_templates.yaml`: Defines default pipelines.
2. `config/workflow/transition_rules.yaml`: Defines global constraints.

## 4. State Transitions

The core of the engine is the `transition_workflow` service method. It supports:
- `forward`: Moving to the next stage. Validates against `transition_rules.yaml`.
- `reject` / `withdraw`: Terminates the workflow instance.

## 5. Event Syncing (Search Integration)

Whenever a workflow transitions, an event is fired in `app/workflow/events/sync.py`.
This event:
1. Pushes a log to the `CandidateTimeline` so users viewing their profile see the workflow update.
2. Pushes a log to the `JobTimeline`.
3. Updates the underlying Search Engine feature vector.

## Future Capability Utilization
This pipeline will quietly exist in the backend until Phase 6, where it could be re-activated to guide users through structured "Career Roadmaps" (e.g., Resume Review -> Skill Building -> Interview Prep).
