# Identity & Access Control Platform

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial Implementation (Phase 3.7) |

## 1. Overview
The Identity platform transforms the ATS into a multi-tenant SaaS application. It introduces robust Role-Based Access Control (RBAC), Organization isolation, and stateless Authentication via JWTs.

## 2. Authentication Flow
- **Algorithms:** Passwords are hashed using Argon2id. Tokens are generated using HS256 JWTs.
- **Access Tokens:** Short-lived (30 minutes) stateless tokens embedded with the `user_id` (`sub`) and a unique token identifier (`jti`).
- **Refresh Tokens:** Long-lived (7 days) stateful tokens saved in the database tied to a `Session`.
- **Revocation:** Since the JWT is technically stateless, revocation is achieved by storing active Sessions in the database and checking the `jti` of the incoming token against the active session list in the Auth Middleware.

## 3. Multi-Tenancy (Organizations)
- Every single user belongs to exactly one root `Organization` (tenant).
- The `org_middleware.py` resolves the organization context from the User's profile or the request headers.
- **Domain Decoupling:** Existing domains (Candidate, Job, Workflow) remain unaffected at the database schema level for MVP. Instead, cross-domain isolation is enforced at the API routing layer through the `org_middleware` which restricts query contexts.

## 4. RBAC Engine
The platform implements a highly granular, policy-driven authorization engine.
- **Roles:** Tied to Organizations. (e.g., "Hiring Manager", "Interviewer").
- **Permissions:** Strings representing actions (e.g., `job.read`, `candidate.write`).
- **Wildcards:** The `AuthorizationService` resolves wildcard permissions. Giving a role `job.*` automatically grants them `job.read`, `job.write`, etc.
- **Resource Guard:** `RequiresPermission("candidate.delete")` acts as a FastAPI dependency, halting the request instantly if the authenticated user lacks the precise role bindings.

## 5. Session Lifecycle
- Upon login, a `Session` record is created logging the `user_agent` and `ip_address`.
- Users can view their active sessions.
- `/auth/logout` flags the session and all associated refresh tokens as `is_revoked = True`.
- `LoginHistory` records track failed brute-force attempts for future Rate Limiting.

## 6. Future Extensions
Because the identity logic is tightly boxed into `app/identity/`, migrating this setup to external identity providers like **Auth0**, **Clerk**, or **WorkOS** in the future would simply involve swapping out the `AuthenticationService` and validating an external JWKS signature inside `auth_middleware.py` instead of the local symmetric secret.
