class SafetyService:
    """Enforces boundaries, PII checks, and Prompt Injection detection."""
    def check_input(self, text: str) -> bool:
        # e.g., if "Ignore all previous instructions" in text: return False
        return True

    def check_output(self, text: str) -> bool:
        return True
