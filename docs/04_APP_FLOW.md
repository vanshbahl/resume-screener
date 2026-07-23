# Application Flow

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.1     | Updated to reflect Phase 1 Architecture |
| 2026-07-23 | 2.2     | Updated to reflect Phase 2.2 Hybrid Pipeline |

## 1. Overall System Architecture
```mermaid
graph TD
    subgraph Frontend [React Web Client - Planned Phase 5]
        UI[User Interface]
        Dashboard[Recruiter Dashboard]
    end

    subgraph Backend [FastAPI Server - Phase 1]
        API[API Router]
        Pipeline[Ingestion Pipeline]
    end

    subgraph DB [Database Layer - Phase 1]
        PG[(PostgreSQL Relational)]
        JSON[(JSONB Metadata)]
    end

    UI -.->|Upload Resume| API
    
    API -->|Save Job/Status| PG
    API -->|Trigger Extraction| Pipeline
    
    Pipeline -->|Store JSON Metadata| JSON
```

## 2. User Journey
```mermaid
journey
    title Recruiter Workflow
    section Job Creation (Phase 1)
      Create Job: 5: Recruiter
    section Ingestion (Phase 1)
      Upload Resumes: 5: Recruiter
      Wait for Processing: 3: Recruiter
    section Evaluation (Phase 4 & 5)
      View Ranked List: 5: Recruiter
```

## 3. Document Processing Pipeline (Phase 2.2.1)
```mermaid
flowchart TD
    A[Resume Upload] --> B[PDF Storage]
    B --> C[PDFExtractionStage]
    C --> D[TextCleaningStage]
    D --> E[SectionDetectionStage]
    
    subgraph EntityExtractionStage [Domain Extractors]
        F1[SkillsExtractor]
        F2[ExperienceExtractor]
        F3[ProjectExtractor]
        F4[EducationExtractor]
    end
    
    E --> EntityExtractionStage
    EntityExtractionStage --> G[SpacyNERStage]
    G --> H[HuggingFaceNERStage]
    H --> I[EntityFusionStage]
    I --> J[NormalizationStage]
    J --> K[ValidationStage]
    K --> L[(Database JSONB)]
```

## 4. Request Lifecycle (Phase 1)
```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant IngestionPipeline
    participant PostgreSQL

    User->>FastAPI: POST /jobs/{id}/resumes/ (PDF)
    FastAPI->>PostgreSQL: INSERT Resume (status: PENDING)
    FastAPI->>IngestionPipeline: extract_and_store()
    FastAPI-->>User: 202 Accepted (Resume ID)
    
    IngestionPipeline->>IngestionPipeline: Extract Text & Clean
    IngestionPipeline->>PostgreSQL: UPDATE structured JSON
    IngestionPipeline->>PostgreSQL: UPDATE status (PROCESSED)
    
    User->>FastAPI: GET /resumes/{id}
    PostgreSQL-->>FastAPI: Resume JSON
    FastAPI-->>User: JSON Response
```
