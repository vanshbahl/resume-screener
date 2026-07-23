# Product Requirements Document (PRD)

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |

## 1. Vision
To build a scalable, offline-capable, and privacy-first Document Intelligence Platform that eliminates the manual burden of parsing and evaluating structured/unstructured documents, beginning with Resume Screening.

## 2. Goals
- Automate resume screening against specific job descriptions.
- Eliminate dependency on paid third-party LLMs (OpenAI, Claude) to ensure data privacy and zero inference costs.
- Lay a generic foundation capable of parsing Invoices and Purchase Orders in the future.

## 3. Scope
**In Scope (MVP):**
- PDF Resume ingestion and text extraction.
- Hard skill extraction and fuzzy matching.
- Dense vector generation for semantic similarity scoring.
- Deterministic ranking engine.
- Local PostgreSQL + pgvector storage.
- Web dashboard for uploading jobs/resumes and viewing scores.

**Out of Scope (MVP):**
- Invoice/PO processing.
- Multi-node distributed workers (Celery).
- Complex authentication (SSO/OAuth).

## 4. User Personas
**1. Recruiter / HR Manager (Primary)**
- Needs to rapidly filter 100s of resumes for a role.
- Wants transparent, explainable scoring metrics.
- Not technical; requires an intuitive web dashboard.

**2. System Administrator (Secondary)**
- Needs an application that is easy to deploy via Docker.
- Prefers offline AI models to comply with company data policies.

## 5. Functional Requirements
- **FR1:** System must allow users to create a Job with a title and list of required skills.
- **FR2:** System must accept PDF uploads for resumes.
- **FR3:** System must extract text, fallback to OCR if necessary, and clean the output.
- **FR4:** System must score the resume based on hard skills and semantic context.
- **FR5:** System must display a ranked list of candidates per job.

## 6. Non-functional Requirements
- **Performance:** A single resume should be processed in under 5 seconds locally.
- **Privacy:** 100% of data processing must occur locally. No data leaves the VPC/Host.
- **Maintainability:** The architecture must adhere to SOLID principles for easy expansion.

## 7. Success Metrics
- 95%+ accurate text extraction on standard PDFs.
- >80% accuracy on skill matching vs manual human review.
- Under 10 seconds total processing time per document on standard CPU hardware.

## 8. Risks
- **Parsing Accuracy:** Highly stylized resumes may break extraction order.
- **Model Size:** Downloading and caching Hugging Face models requires significant initial bandwidth and disk space.

## 9. Feature Status
- ✅ Basic PDF Upload & Text Extraction
- ✅ Deterministic Parsing Rules
- ✅ Hybrid AI Parsing (spaCy + Hugging Face)
- ✅ Automated Parser Benchmarking
- ✅ Deterministic Candidate Matching & Ranking (Phase 2)
- ✅ Search & Retrieval Engine (Phase 2)
- ✅ Configurable Recommendation & Decision Engine (Phase 2)
- 🟡 Local pgvector setup (Phase 3)
- ⚪ Dashboard & UI (Phase 5)

## 10. Future Scope
- Generic Invoice and Purchase order parsing using GLiNER (Zero-shot NER).
- Advanced BI Analytics dashboard.
- Email integration to auto-ingest resumes from an inbox.
