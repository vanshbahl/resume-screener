# Identity & Access Control Platform

## Revision History
| Date       | Version | Description                   |
| ---------- | ------- | ----------------------------- |
| 2026-07-23 | 1.0     | Initial Implementation (Phase 3.7) |
| 2026-07-26 | 2.0     | B2C User Accounts Focus |

## 1. Overview
The Identity platform serves as the foundational **Supporting Infrastructure** for User Accounts on the Resume Intelligence Platform. It provides stateless Authentication via JWTs, robust Role-Based Access Control (RBAC), and preserves an Organization structure for future capabilities.

## 2. Authentication Flow
- **Algorithms:** Passwords are hashed using Argon2id. Tokens are generated using HS256 JWTs.
- **Access Tokens:** Short-lived (30 minutes) stateless tokens embedded with the `user_id` (`sub`) and a unique token identifier (`jti`).
- **Refresh Tokens:** Long-lived (7 days) stateful tokens saved in the database tied to a `Session`.
- **Revocation:** Since the JWT is technically stateless, revocation is achieved by storing active Sessions in the database and checking the `jti` of the incoming token against the active session list in the Auth Middleware.

## 3. Organizations (Future Capability)
- Every single user belongs to exactly one root `Organization` (tenant).
- While the platform is currently B2C (where each user might just be in their own isolated organization), this multi-tenant architecture is intentionally preserved to support future B2B features like **University Cohorts** or Team Collaboration.
- The `org_middleware.py` resolves the organization context from the User's profile or the request headers.

## 4. RBAC Engine
The platform implements a highly granular, policy-driven authorization engine.
- **Roles:** Tied to Organizations.
- **Permissions:** Strings representing actions (e.g., `resume.read`, `resume.write`).
- **Wildcards:** The `AuthorizationService` resolves wildcard permissions. Giving a role `resume.*` automatically grants them `resume.read`, `resume.write`, etc.
- **Resource Guard:** `RequiresPermission("resume.delete")` acts as a FastAPI dependency, halting the request instantly if the authenticated user lacks the precise role bindings.

## 5. Session Lifecycle
- Upon login, a `Session` record is created logging the `user_agent` and `ip_address`.
- Users can view their active sessions.
- `/auth/logout` flags the session and all associated refresh tokens as `is_revoked = True`.
- `LoginHistory` records track failed brute-force attempts for future Rate Limiting.

## 6. Future Extensions
Because the identity logic is tightly boxed into `app/identity/`, migrating this setup to external identity providers like **Auth0**, **Clerk**, or **WorkOS** in the future would simply involve swapping out the `AuthenticationService` and validating an external JWKS signature inside `auth_middleware.py` instead of the local symmetric secret.
