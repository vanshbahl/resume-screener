# Product Requirements Document (PRD)

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |
| 2026-07-23 | 2.5     | Updated to reflect Phase 3 ATS completion |

## 1. Vision
To build a scalable, offline-capable, and privacy-first Document Intelligence Platform and Applicant Tracking System (ATS) that eliminates the manual burden of sourcing, tracking, and evaluating candidates throughout the entire hiring lifecycle.

## 2. Goals
- Automate resume screening against specific job descriptions.
- Eliminate dependency on paid third-party LLMs (OpenAI, Claude) to ensure data privacy and zero inference costs.
- Provide a robust Enterprise Backend supporting Candidates, Jobs, Workflows, Interviews, and Analytics.
- Lay a generic foundation capable of parsing Invoices and Purchase Orders in the future.

## 3. Scope
**In Scope (MVP):**
- PDF Resume ingestion and hybrid AI text extraction.
- Hard skill extraction, dense vector generation, and semantic similarity scoring.
- Deterministic candidate ranking and recommendation engine.
- Complete ATS Backend (Jobs, Candidates, Workflows, Interviews, Workspaces, Analytics).
- Local PostgreSQL + pgvector storage.
- Automated CI/CD Testing Infrastructure.

**Out of Scope (MVP):**
- Complex frontend web dashboard (Planned for Phase 5).
- Multi-node distributed workers (Celery).
- Invoice/PO processing.

## 4. User Personas
**1. Recruiter / HR Manager (Primary)**
- Needs to rapidly filter 100s of resumes for a role and track them across a custom hiring pipeline.
- Requires transparent, explainable scoring metrics.
- Utilizes customized analytics dashboards and CSV reports.

**2. System Administrator (Secondary)**
- Needs an application that is easy to deploy via Docker and test via CI/CD.
- Prefers offline AI models to comply with strict internal data policies.

## 5. Functional Requirements
- **FR1:** System must allow users to create Jobs with specific requirements and track Candidates applying to them.
- **FR2:** System must extract text from resumes, utilize local NLP to parse entities, and map them to Candidate Profiles.
- **FR3:** System must execute semantic similarity scoring and heuristic gap analysis.
- **FR4:** System must manage Candidates moving through dynamic Workflow Pipelines (e.g. Screen -> Technical -> Offer).
- **FR5:** System must manage Interview scheduling, panel mapping, and JSONB scorecards.
- **FR6:** System must provide cross-domain Analytics (Time-to-Hire, Conversion Rates).

## 6. Non-functional Requirements
- **Performance:** Complex aggregations must be locally cached to ensure fast dashboard load times.
- **Privacy:** 100% of data processing must occur locally. No data leaves the VPC/Host.
- **Maintainability:** The architecture must adhere to strict Domain-Driven Design (DDD) to support future RBAC.

## 7. Success Metrics
- Fully isolated domains working in harmony with zero duplicate logic.
- >80% accuracy on skill matching vs manual human review.
- API requests execute efficiently with scalable database indexing and cached read models.

## 8. Risks
- **Model Size:** Downloading and caching Hugging Face models requires significant initial bandwidth and disk space.
- **Complexity:** Keeping decoupled domains synchronized requires careful timeline and event logging.

## 9. Feature Status
- ✅ Basic PDF Upload & Text Extraction
- ✅ Hybrid AI Parsing (spaCy + Hugging Face)
- ✅ Automated Parser Benchmarking
- ✅ Deterministic Candidate Matching & Ranking
- ✅ Configurable Recommendation & Decision Engine
- ✅ Candidate & Job Management Domains
- ✅ Configurable Workflow Pipelines & Timeline Audit Logging
- ✅ Interview Management (Logistics, Scorecards)
- ✅ Recruiter Workspace & Caching
- ✅ Analytics & Reporting Platform (Dashboards, CSV Exports)
- ⚪ Organizations & RBAC (Multi-Tenancy)
- ⚪ Frontend React Dashboard (Phase 5)

## 10. Future Scope
- Multi-tenant RBAC platform capabilities.
- Generic Invoice and Purchase order parsing using GLiNER.
- Real-time event-sourcing for extreme analytic scaling.
