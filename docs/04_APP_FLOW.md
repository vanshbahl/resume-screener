# Application Flow

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |

## 1. Overall System Architecture
```mermaid
graph TD
    subgraph Frontend [React Web Client]
        UI[User Interface]
        Dashboard[Recruiter Dashboard]
    end

    subgraph Backend [FastAPI Server]
        API[API Router]
        Pipeline[Background AI Pipeline]
        Scoring[Scoring Engine]
    end

    subgraph DB [Database Layer]
        PG[(PostgreSQL Relational)]
        JSON[(JSONB Metadata)]
        Vec[(pgvector Embeddings)]
    end

    UI -->|Upload Resume| API
    Dashboard -->|Query Rankings| API
    
    API -->|Save Job/Status| PG
    API -->|Trigger Task| Pipeline
    
    Pipeline -->|Store Entities| JSON
    Pipeline -->|Store Vectors| Vec
    
    Scoring -->|Fuzzy Match| JSON
    Scoring -->|Cosine Similarity| Vec
    Scoring -->|Update Score| PG
```

## 2. User Journey
```mermaid
journey
    title Recruiter Workflow
    section Job Creation
      Create Job: 5: Recruiter
      Define Required Skills: 4: Recruiter
    section Ingestion
      Drag & Drop Resumes: 5: Recruiter
      Wait for Processing: 3: Recruiter
    section Evaluation
      View Ranked List: 5: Recruiter
      Analyze Candidate Score Breakdown: 4: Recruiter
```

## 3. Document Processing Pipeline
```mermaid
flowchart TD
    A[Upload PDF] --> B(FastAPI Endpoint)
    B --> C{PyMuPDF Extraction}
    C -->|Text found| D[Clean Text - spaCy]
    C -->|Sparse text| E[PaddleOCR Extraction]
    E --> D
    
    D --> F[Fuzzy Match Skills - RapidFuzz]
    D --> G[Generate Embeddings - bge-small]
    
    F --> H[Save to JSONB]
    G --> I[Save to pgvector]
    
    H --> J(Calculate Final Score)
    I --> J
```

## 4. Request Lifecycle
```mermaid
sequenceDiagram
    participant User
    participant FastAPI
    participant BackgroundWorker
    participant PostgreSQL

    User->>FastAPI: POST /jobs/{id}/resumes/ (PDF)
    FastAPI->>PostgreSQL: INSERT Resume (status: PENDING)
    FastAPI->>BackgroundWorker: Enqueue process_resume_background()
    FastAPI-->>User: 202 Accepted (Resume ID)
    
    BackgroundWorker->>BackgroundWorker: Extract Text & Run AI
    BackgroundWorker->>PostgreSQL: UPDATE parsed_metadata & embedding
    BackgroundWorker->>BackgroundWorker: score_resume()
    BackgroundWorker->>PostgreSQL: UPDATE final_score (status: PROCESSED)
    
    User->>FastAPI: GET /jobs/{id}/rankings/
    FastAPI->>PostgreSQL: SELECT Resumes ORDER BY final_score DESC
    PostgreSQL-->>FastAPI: Ranked List
    FastAPI-->>User: JSON Response
```
