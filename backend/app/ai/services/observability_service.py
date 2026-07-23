from app.ai.repositories.ai_repo import AIRepository
from app.ai.models.base_models import AITrace, AICost

class ObservabilityService:
    """Tracks latency, tokens, cost, and stores traces."""
    def __init__(self, repo: AIRepository):
        self.repo = repo

    def log_trace(
        self, 
        org_id: str, 
        message_id: str, 
        provider: str, 
        model: str, 
        latency_ms: float, 
        tokens: int,
        request_payload: dict,
        response_payload: dict
    ):
        trace = AITrace(
            organization_id=org_id,
            message_id=message_id,
            provider=provider,
            model=model,
            latency_ms=latency_ms,
            prompt_tokens=tokens,
            completion_tokens=0,
            total_tokens=tokens,
            request_payload=request_payload,
            response_payload=response_payload
        )
        self.repo.create_trace(trace)
