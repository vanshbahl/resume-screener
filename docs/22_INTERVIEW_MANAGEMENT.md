# Interview Management Domain (Phase 3.5)

The **Interview Management Domain** owns the entire lifecycle of an interview, serving as the scheduling, evaluating, and coordination backend for the Applicant Tracking System.

## Architecture & Entities

This domain is completely decoupled from the Workflow engine's internal logic, interacting purely through synchronized `TimelineEvents` or by invoking the Workflow service directly on definitive outcomes (e.g., rejecting a candidate).

### Core Models
- **`Interview`**: Represents the interview instance. Maps 1:1 with a Candidate and Job. 
- **`InterviewSchedule`**: Handles logistical timing, meeting links, and locations. Validates that `end_time` strictly follows `start_time`.
- **`InterviewPanel`**: Maps specific users to the interview and their expected roles (e.g., `Lead`, `Shadow`).
- **`InterviewFeedback`**: Aggregates a single interviewer's qualitative assessment (strengths, weaknesses, overall recommendation).
- **`InterviewScorecard`**: Attached to `Feedback`, utilizing a `JSONB` criteria column to allow highly configurable templates without strict DDL constraints.
- **`InterviewTemplate`**: Configuration profiles allowing organizations to pre-define duration, standard panel requirements, and scorecard structures based on `interview_type`.

## Lifecycle

1. **Creation**: An interview is instantiated (optionally from a Template).
2. **Panel Assignment**: Interviewers are assigned via the `/panel` endpoint.
3. **Scheduling**: A schedule is mapped, emitting a `TimelineEvent` indicating the interview is formally planned.
4. **Execution**: During/After the interview, panel members submit their `Feedback` and `Scorecard`.
5. **Completion**: A recruiter or hiring manager reviews the feedback and invokes the `/complete` endpoint, marking an `outcome`. If the outcome is definitive (e.g., `FAIL`), it triggers a workflow stage transition automatically.

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

## Future Extensions
Because the scheduling schema separates `timezone` and generic string-based `meeting_url`s, implementing OAuth-based Google Calendar or Outlook synchronization simply involves a background worker calling the `SchedulingService` and mapping the generated payload back to the DB schema.
