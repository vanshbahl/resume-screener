# Backend Schema & Architecture

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |

## 1. Folder Structure
```text
/backend
├── app/
│   ├── api/             # HTTP endpoints and routing
│   ├── core/            # Config, DB connection, Skills dictionary
│   ├── models/          # SQLAlchemy table definitions
│   ├── schemas/         # Pydantic data validation (Request/Response)
│   ├── services/        # Business logic, OCR, NLP pipelines
│   └── main.py          # FastAPI application entry point
```

## 2. Entity Relationships (ER Diagram)
```mermaid
erDiagram
    JOB ||--o{ RESUME : "receives"
    RESUME ||--|| RESUME_EMBEDDING : "has one"

    JOB {
        int id PK
        string title
        text description
        json required_skills
        datetime created_at
    }

    RESUME {
        int id PK
        int job_id FK
        string filename
        string status "PENDING, PROCESSED, ERROR"
        text raw_text
        jsonb parsed_metadata "Contains extracted skills"
        float final_score
        datetime created_at
    }

    RESUME_EMBEDDING {
        int id PK
        int resume_id FK
        text chunk_text
        vector embedding "(dim: 384)"
    }
```

## 3. Database Tables
- **jobs**: Stores the target job requirements.
- **resumes**: Uses a flexible `JSONB` column (`parsed_metadata`) to avoid complex relational joins for dynamic data like skills and education.
- **resume_embeddings**: Uses the `pgvector` extension. A `VECTOR` type is used to execute native cosine similarity searches inside the DB.

## 4. API Modules
- `POST /jobs/`: Create a new job requirement.
- `GET /jobs/`: Retrieve all active jobs.
- `POST /jobs/{id}/resumes/`: Upload a resume document for a job.
- `GET /jobs/{id}/rankings/`: Retrieve a sorted list of scored candidates.

## 5. AI Modules & Services
```mermaid
classDiagram
    class PipelineService {
        +process_resume(file_path) dict
        +clean_text(text) str
        +extract_skills(text) list
        +generate_embeddings(text) vector
    }
    class ExtractionService {
        +extract_text_from_pdf(file_path) str
        +extract_text_with_ocr(file_path) str
    }
    class ScoringService {
        +score_resume(job_skills, resume_skills, job_embedding, resume_embedding) float
        +cosine_similarity(vec1, vec2) float
    }

    PipelineService --> ExtractionService : Uses for Text
    PipelineService --> ScoringService : Calls to calculate score
```

## 6. Storage
- **Relational**: PostgreSQL.
- **Documents**: Uploaded PDFs are temporarily stored on local disk (`/uploads`) until processed.
- **Models**: Hugging Face models are cached natively in `~/.cache/huggingface` by default.
