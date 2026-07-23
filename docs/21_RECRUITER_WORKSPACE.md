# Recruiter Workspace (Phase 3.4)

The **Recruiter Workspace** is the core entry point for talent acquisition operations. Rather than duplicating existing Candidate and Job logic, it acts as an **Orchestration and Aggregation** layer over the existing Domain-Driven systems.

## Architecture

The Workspace is composed of several high-level services that consume underlying Domain models:

1. **DashboardService**: Aggregates open jobs, active pipelines, and system-wide metrics.
2. **WorkQueueService**: Sorts and filters Candidate and Job pipelines into actionable segments (e.g. "Pending Review", "Interviews Today").
3. **ActivityFeedService**: Consolidates `TimelineEvent` objects from candidates, jobs, and workflows into a unified Chronological feed.
4. **SavedSearchService / FavoriteService**: Provides personalization and bookmarks for recruiters.
5. **QuickActionService**: Normalizes common operations (like advancing a candidate stage) and proxies them to the `WorkflowService` or `CandidateService`.
6. **AnalyticsService**: Exposes lightweight recruiter-level throughput metrics.

## Caching

To ensure snappy performance, the Workspace employs a unified caching interface (`CacheRepository`).
Currently, this is backed by an in-memory python dictionary implementation (`MemoryCacheRepository`) to remove local testing dependencies. 

Because it adheres to standard `get/set/clear` interfaces, dropping in `Redis` for distributed production environments requires zero changes to the services themselves.

## API Endpoints

All endpoints are grouped under `/workspace/`:
- `GET /workspace/dashboard`
- `GET /workspace/activity`
- `GET /workspace/queue/candidates`
- `GET /workspace/queue/jobs`
- `GET /workspace/notifications`
- `PATCH /workspace/preferences`
- `GET / POST / DELETE /workspace/searches`
- `GET / POST /workspace/favorites`
- `POST /workspace/actions/advance-workflow`
- `GET /workspace/analytics`

## Future Compatibility

This schema ensures we are ready to scale to:
- Mobile Application views.
- Redis-backed distributed caches.
- Granular WebSocket Notification streams.
- Multi-tenant organization support.
