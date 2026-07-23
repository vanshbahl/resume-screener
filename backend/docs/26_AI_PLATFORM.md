# AI Platform & Copilot

The AI Platform provides orchestration, context management, memory, safety, and tool execution for intelligent agents within the Recruitment Intelligence Platform.

## Architecture Principles

1. **Provider Agnostic:** Interactions with external models are abstracted behind `LLMProvider` and `EmbeddingProvider` interfaces.
2. **Deterministic Fallback:** AI never replaces core business logic. Agents orchestrate deterministic domain services via the `ToolRegistry`.
3. **Data Segregation:** The `ContextBuilder` ensures all information injected into prompts complies with strict Role-Based Access Control (RBAC) and Multi-Tenancy (Organization ID isolation).
4. **Observable:** Every interaction logs a trace (`AITrace`) and cost metrics (`AICost`) for auditing and optimization.

## Core Components

- **AgentOrchestrator:** A multi-step execution loop that evaluates LLM responses, invokes requested tools, appends results to history, and resubmits to the LLM until a final response is derived.
- **MemoryManager:** Handles long-term memory via the database, retrieving past `AIConversation` and `AIMessage` data to formulate history.
- **ContextBuilder:** Constructs a strict context payload for system prompts (e.g., retrieving Candidate or Job data constrained by User/Org permissions).
- **ToolRegistry:** Maps intent schemas (like `search_candidates` or `schedule_interview`) to underlying deterministic business domain services.
- **PromptTemplateService:** Version-controlled database-backed prompt templates for dynamic prompt rendering using Jinja2 formatting.
- **FeedbackService:** Captures explicit user feedback (`AIFeedback`) on AI responses to enable RLHF/fine-tuning pipelines.

## Database Models

- `AIConversation`: Tracks individual chat sessions, agent types, and bound context variables.
- `AIMessage`: Sequenced records of User, Assistant, System, and Tool messages.
- `AIPromptTemplate`: Versioned records of prompts (global or org-specific).
- `AIFeedback`: Ratings and comments on specific assistant messages.
- `AITrace`: Observability logs storing raw inputs/outputs, model info, token usage, and latency.
- `AICost`: Financial rollup logs aggregating provider-specific token costs.

## Security

All routes and internal context building mandate execution within an authenticated session, passing both `user_id` and `organization_id` down to the domain repositories to guarantee isolation.
