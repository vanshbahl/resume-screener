from typing import Dict, Any, Callable, List
import json
from app.ai.schemas.schemas import ToolSchema, ToolSchemaFunction, ToolSchemaParameters, ToolSchemaProperty
from sqlalchemy.orm import Session
# Imports to existing domain services would go here
# from app.candidate.services.candidate_service import CandidateService

class ToolRegistry:
    """Manages tools available to the AI, exposing schemas and executing intents."""
    def __init__(self, db: Session):
        self.db = db
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        # 1. Search Candidates Tool
        self._register_tool(
            name="search_candidates",
            description="Search for candidates in the ATS by keywords or skills.",
            parameters={
                "query": ToolSchemaProperty(type="string", description="Keywords to search for")
            },
            required=["query"],
            executor=self._execute_search_candidates
        )
        
        # 2. Get Job Details Tool
        self._register_tool(
            name="get_job_details",
            description="Retrieve details for a specific job posting.",
            parameters={
                "job_id": ToolSchemaProperty(type="string", description="The ID of the job")
            },
            required=["job_id"],
            executor=self._execute_get_job_details
        )

    def _register_tool(
        self, 
        name: str, 
        description: str, 
        parameters: Dict[str, ToolSchemaProperty], 
        required: List[str], 
        executor: Callable
    ):
        schema = ToolSchema(
            function=ToolSchemaFunction(
                name=name,
                description=description,
                parameters=ToolSchemaParameters(
                    properties=parameters,
                    required=required
                )
            )
        )
        self._tools[name] = {
            "schema": schema,
            "executor": executor
        }

    def get_schemas(self) -> List[ToolSchema]:
        return [t["schema"] for t in self._tools.values()]

    def execute_tool(self, name: str, arguments_json: str, org_id: str, user_id: str) -> str:
        """
        Executes a registered tool, guaranteeing RBAC through the underlying service or passing org_id.
        """
        if name not in self._tools:
            return f"Error: Tool '{name}' not found."
            
        try:
            kwargs = json.loads(arguments_json)
        except json.JSONDecodeError:
            return "Error: Invalid JSON arguments provided to tool."
            
        try:
            # Execute the deterministic tool
            result = self._tools[name]["executor"](org_id=org_id, user_id=user_id, **kwargs)
            # In a real system, we'd json.dumps the resulting Pydantic models
            return json.dumps(result)
        except Exception as e:
            return f"Error executing tool: {str(e)}"

    # --- Tool Implementations (Delegating to deterministic domains) ---
    def _execute_search_candidates(self, org_id: str, user_id: str, query: str) -> Dict[str, Any]:
        # Here we would call the Search Service. Stubbing for now.
        return {"status": "success", "results": [f"Candidate matching '{query}'"]}

    def _execute_get_job_details(self, org_id: str, user_id: str, job_id: str) -> Dict[str, Any]:
        # Here we would call JobService.
        return {"status": "success", "job_title": "Software Engineer", "job_id": job_id}
