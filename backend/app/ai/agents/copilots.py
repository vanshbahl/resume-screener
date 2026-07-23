from app.ai.agents.base import AgentOrchestrator

class RecruiterCopilot(AgentOrchestrator):
    """
    Specifically configured for Recruiters.
    Has access to Search, Workflow, and Candidate Lookup tools.
    """
    pass

class HiringManagerCopilot(AgentOrchestrator):
    """
    Specifically configured for Hiring Managers.
    Has access to Interview Feedback, Job Requisition statuses.
    """
    pass

class InterviewCopilot(AgentOrchestrator):
    """
    Used during or after interviews to summarize scorecards.
    """
    pass
