# Product Requirements Document (PRD)

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial MVP Document Creation |
| 2026-07-26 | 3.0     | Shifted vision to Resume Intelligence Platform |

## 1. Vision
To build a scalable, offline-capable, and privacy-first AI Resume Intelligence Platform that empowers students and job seekers to understand how competitive their resume is compared to industry expectations, bypassing the "ATS black box" with transparent, actionable feedback.

## 2. Goals
- Provide intelligent parsing, scoring, and benchmarking for uploaded resumes.
- Offer personalized feedback and AI follow-up questions for missing resume sections.
- Eliminate dependency on paid third-party LLMs (OpenAI, Claude) to ensure data privacy and zero inference costs.
- Provide a robust backend supporting the core intelligence engine, with scalable infrastructure for user accounts, notifications, and analytics.
- Lay a generic foundation capable of advanced career insights and resume optimization in the future.

## 3. Scope
**In Scope (Current Product):**
- PDF Resume ingestion and hybrid AI text extraction.
- Hard skill extraction, dense vector generation, and semantic similarity scoring.
- Resume intelligence reporting, scoring, and benchmarking.
- Robust backend infrastructure (User Accounts, Platform Analytics, Notifications).
- Local PostgreSQL + pgvector storage.
- Automated CI/CD Testing Infrastructure.

**Out of Scope (MVP):**
- Complex B2B/Enterprise hiring pipelines (Implemented in backend schema but not exposed in primary UI).
- Real-time Mock Interviews (Implemented in backend schema but scheduled for future phases).

## 4. User Personas
**1. Student / Job Seeker (Primary)**
- Needs to rapidly evaluate their resume's strength against industry benchmarks.
- Requires transparent, explainable scoring metrics and actionable recommendations.
- Utilizes the platform to uncover missing skills or formatting issues before applying for jobs.

**2. System Administrator (Secondary)**
- Needs an application that is easy to deploy via Docker and test via CI/CD.
- Prefers offline AI models to comply with strict internal data policies.

## 5. Functional Requirements
- **FR1:** System must allow users to upload their resume for processing.
- **FR2:** System must extract text from resumes, utilize local NLP to parse entities, and generate structured profiles.
- **FR3:** System must execute semantic similarity scoring, identify gaps, and intelligently ask follow-up questions for missing information.
- **FR4:** System must generate an overall score, highlight strengths/weaknesses, and rank the resume against the dataset.
- **FR5:** System must provide robust authentication, account management, and platform notifications.

## 6. Non-functional Requirements
- **Performance:** Vector rankings and parsing must execute efficiently to ensure fast dashboard load times.
- **Privacy:** 100% of data processing must occur locally. No data leaves the VPC/Host.
- **Maintainability:** The architecture must adhere to strict Domain-Driven Design (DDD) to support future features.

## 7. Success Metrics
- Fully isolated domains working in harmony with zero duplicate logic.
- High accuracy on skill extraction and benchmarking recommendations.
- API requests execute efficiently with scalable database indexing and cached read models.

## 8. Risks
- **Model Size:** Downloading and caching Hugging Face models requires significant initial bandwidth and disk space.
- **Complexity:** Managing the transition of parsed data through the scoring pipelines requires robust architectural boundaries.

## 9. Feature Status
### Current Product
- ✅ Basic PDF Upload & Text Extraction
- ✅ Hybrid AI Parsing (spaCy + Hugging Face)
- ✅ Automated Parser Benchmarking
- ✅ Resume Benchmarking & Ranking (Search Engine)
- ✅ AI Feedback & Follow-ups (Copilot Platform)
- ⚪ Resume Intelligence Frontend (Phase 4)

### Supporting Infrastructure
- ✅ User Workspace (Dashboards & Caching)
- ✅ Resume Intelligence Analytics (Dashboards, CSV Exports)
- ✅ User Accounts & Identity (Multi-Tenancy & RBAC)
- ✅ User Notifications (Communication Hub)

### Future Capabilities (Implemented Backend)
- ✅ Internal Processing Pipelines (Workflow Engine)
- ✅ Future Mock Interview Platform (Interview Management)
- ✅ Job Description Benchmarking Engine (Job Management)

## 10. Future Scope
- Frontend User Interface construction.
- Resume optimization, job-specific rewriting, and career roadmaps.
- Future mock interview platform leveraging existing interview schemas.
