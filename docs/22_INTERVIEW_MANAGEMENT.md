# Phase 3.5: Future Mock Interview Platform

The Interview Management Domain is fully implemented in the backend, but is currently categorized as a **Future Capability** for the Resume Intelligence Platform.

Originally designed for recruiter scheduling, this robust schema is preserved to power a future **Mock Interview Platform** where users can schedule AI-driven or peer-to-peer practice interviews.

## Architecture & Entities

This domain is completely decoupled from the Workflow engine's internal logic, interacting purely through synchronized `TimelineEvents`.

### Core Models
- **`Interview`**: Represents the interview instance. Maps 1:1 with a User and a target Job Benchmark. 
- **`InterviewSchedule`**: Handles logistical timing, meeting links, and locations.
- **`InterviewPanel`**: Maps specific users or AI agents to the interview and their expected roles.
- **`InterviewFeedback`**: Aggregates qualitative assessment (strengths, weaknesses, overall recommendation).
- **`InterviewScorecard`**: Attached to `Feedback`, utilizing a `JSONB` criteria column to allow highly configurable templates without strict DDL constraints.
- **`InterviewTemplate`**: Configuration profiles allowing pre-defined duration and scorecard structures based on `interview_type`.

## Lifecycle

1. **Creation**: An interview is instantiated (optionally from a Template).
2. **Panel Assignment**: Interviewers (AI or Peer) are assigned via the `/panel` endpoint.
3. **Scheduling**: A schedule is mapped, emitting a `TimelineEvent` indicating the interview is formally planned.
4. **Execution**: During/After the interview, panel members submit their `Feedback` and `Scorecard`.
5. **Completion**: The user reviews the feedback, generating an overall score.

## API Structure
All logic operates through the `/interviews` router with highly normalized nested resources:
- `POST /interviews`
- `GET /interviews/{id}`
- `PATCH /interviews/{id}`
- `POST /interviews/{id}/schedule`
- `POST /interviews/{id}/panel`
- `DELETE /interviews/{id}/panel/{user_id}`
- `POST /interviews/{id}/feedback`
- `POST /interviews/{id}/complete`

## Future Capability Utilization
This module is not exposed in the primary Phase 4 B2C UI, but remains active in the backend for future expansion into comprehensive career preparation services.
