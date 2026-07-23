# Analytics & Reporting Platform (Phase 3.6)

The **Analytics Platform** sits at the top level of the ATS hierarchy, querying and aggregating transactional data from Candidates, Jobs, Workflows, Interviews, and Workspaces to produce real-time insights and exportable reports.

## Architecture

The Analytics system adheres to the overall Domain-Driven Design (DDD) of the platform but is unique in that it performs read-heavy cross-domain aggregations.

### Core Modules
- **`AnalyticsRepository`**: Performs direct SQLAlchemy aggregations (`func.count`, date filtering) against foreign domains.
- **`KPIService`**: Calculates high-level scalars (Time to Hire, Offer Acceptance Rate).
- **`TrendService`**: Calculates time-series distributions (Hires Over Time, Active Jobs By Month).
- **`DashboardService`**: Allows saving of customized UI layouts via `DashboardConfig`.
- **`ReportService`**: Provides structured tabular queries (Candidate Pipeline, Job Status).
- **`ExportService`**: Converts `ReportService` responses into downloadable CSVs.

## Caching Strategy

Analytics queries can be expensive on a heavily utilized transactional DB. 
To mitigate this, the `AnalyticsService` facade uses the application's global `MemoryCache` interface.

```python
cache_key = "analytics:core_kpis"
cached = self.cache.get(cache_key)
if cached:
    return KPIResponse.model_validate(cached)
```
*Future iterations can seamlessly swap `MemoryCache` with `RedisCache` by changing the dependency injection, without modifying analytics logic.*

## Data Export

Rather than heavily coupling data extraction to third-party libraries like `pandas`, the MVP relies on Python's native `csv` stream serialization.
1. The client requests a tabular JSON report (`/analytics/reports/candidate`).
2. If they need a CSV, they hit the `/export` endpoint with the exact same filter body.
3. The server generates the tabular data, converts it via `io.StringIO` and `csv.writer`, and returns a `PlainTextResponse(media_type="text/csv")`.

## Future Expansion
- **Real-time Event Sourcing:** Currently, aggregations are pulled. In a future hyper-scale version, we can push `TimelineEvents` to a dedicated OLAP database (ClickHouse or Snowflake).
- **PowerBI / Tableau Integration:** The raw `/analytics/reports` endpoints already serve perfectly structured JSON suitable for direct ingestion into BI tools.
