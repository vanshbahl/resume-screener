# Phase 3.4: User Workspace

The **User Workspace** is part of the **Supporting Infrastructure** for the AI Resume Intelligence Platform. It acts as an orchestration and aggregation layer, feeding data to the user's dashboard.

## Architecture

The Workspace is composed of several high-level services that consume underlying Domain models:

1. **DashboardService**: Aggregates the user's active processing pipelines and system-wide notifications.
2. **WorkQueueService**: Sorts and filters active processes (e.g. "Awaiting AI Follow-up", "Completed Reports").
3. **ActivityFeedService**: Consolidates `TimelineEvent` objects from profiles, benchmarks, and workflows into a unified chronological feed.
4. **SavedSearchService / FavoriteService**: Provides personalization and bookmarks for users.
5. **QuickActionService**: Normalizes common operations and proxies them to the appropriate domain service.
6. **AnalyticsService**: Exposes lightweight user-level engagement metrics.

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
