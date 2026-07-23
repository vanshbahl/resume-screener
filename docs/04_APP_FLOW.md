# Application Flow

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 2.5     | Updated to reflect Phase 3 Domain Architecture |

## 1. Overall System Architecture
```mermaid
graph TD
    subgraph Frontend [React Web Client - Planned Phase 5]
        UI[User Interface]
        Dash[Recruiter Dashboards]
    end

    subgraph API [FastAPI Server - Core API]
        R1[Candidate Router]
        R2[Job Router]
        R3[Workflow Router]
        R4[Interview Router]
        R5[Analytics Router]
    end

    subgraph Domains [Business Logic]
        C[Candidate Service]
        J[Job Service]
        W[Workflow Engine]
        I[Interview Logistics]
        A[Analytics Aggregator]
        INT[Intelligence & Parsing Engine]
    end

    subgraph Database [PostgreSQL]
        PG[(Relational Data)]
        JS[(JSONB Artifacts)]
        VEC[(PGVector)]
    end

    UI --> API
    API --> Domains
    Domains --> Database
    C & J <--> INT
    W --> C & J
    I --> W
    A --> W & I & C & J
```

## 2. Core Object Lifecycle
```mermaid
journey
    title Candidate Hiring Journey
    section Ingestion
      Parser extracts Resume: 5: Candidate
      Vector Mapping & Intelligence: 5: System
    section Workflow Pipeline
      Candidate enters Job Pipeline: 5: Recruiter
      Moved to Technical Screen: 4: Recruiter
    section Interview
      Schedule Interview: 4: Recruiter
      Interviewer fills JSON Scorecard: 5: Interviewer
    section Hire
      Final Decision Engine: 5: System
      Analytics & KPIs update: 5: System
```

## 3. Workflow Engine State Transitions
```mermaid
stateDiagram-v2
    [*] --> Applied
    Applied --> Screening
    Screening --> Interview
    Interview --> Offer
    Interview --> Rejected
    Offer --> Hired
    Offer --> Withdrawn
    Hired --> [*]
    Rejected --> [*]
    Withdrawn --> [*]
```

## 4. Analytics Aggregation Flow
```mermaid
sequenceDiagram
    participant Client
    participant AnalyticsRouter
    participant AnalyticsService
    participant MemoryCache
    participant Database

    Client->>AnalyticsRouter: GET /analytics/kpis
    AnalyticsRouter->>AnalyticsService: get_core_kpis()
    AnalyticsService->>MemoryCache: Check "analytics:core_kpis"
    
    alt Cache Miss
        MemoryCache-->>AnalyticsService: None
        AnalyticsService->>Database: Execute Cross-Domain Aggregations
        Database-->>AnalyticsService: Raw Metrics
        AnalyticsService->>AnalyticsService: Compute KPIs
        AnalyticsService->>MemoryCache: Set Cache (300s TTL)
    else Cache Hit
        MemoryCache-->>AnalyticsService: JSON Payload
    end
    
    AnalyticsService-->>AnalyticsRouter: KPIResponse
    AnalyticsRouter-->>Client: 200 OK
```

## 5. Document Processing Pipeline (Intelligence Core)
```mermaid
flowchart TD
    A[Resume Upload] --> B[PDFExtractionStage]
    B --> C[TextCleaningStage]
    C --> D[SectionDetectionStage]
    
    subgraph EntityExtractionStage [Domain Extractors]
        F1[SkillsExtractor]
        F2[ExperienceExtractor]
    end
    
    D --> EntityExtractionStage
    EntityExtractionStage --> G[SpacyNERStage]
    G --> H[HuggingFaceNERStage]
    H --> I[EntityFusionStage]
    I --> J[NormalizationStage]
    J --> K[(Database JSONB & Vectors)]
```
