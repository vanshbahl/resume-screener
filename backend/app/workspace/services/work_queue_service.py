from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.job.models.job import Job
from app.workflow.models.workflow import WorkflowInstance

class WorkQueueService:
    def __init__(self, db: Session):
        self.db = db

    def get_candidates_awaiting_review(self) -> List[Dict[str, Any]]:
        # Fetch pipeline instances in 'APPLIED' or 'SCREENING' stage
        instances = self.db.query(WorkflowInstance).filter(
            # Simplified for schema
            WorkflowInstance.status == "active"
        ).all()
        
        results = []
        for inst in instances:
            results.append({
                "pipeline_id": inst.id,
                "candidate_id": inst.candidate_id,
                "job_id": inst.job_id,
                "stage": inst.current_stage_id,
                "updated_at": inst.updated_at
            })
        return results

    def get_high_priority_jobs(self) -> List[Dict[str, Any]]:
        # Fetch open jobs
        jobs = self.db.query(Job).filter(Job.status == "OPEN").limit(10).all()
        results = []
        for job in jobs:
            results.append({
                "job_id": job.id,
                "title": job.title,
                "department": job.department,
                "created_at": job.created_at
            })
        return results
