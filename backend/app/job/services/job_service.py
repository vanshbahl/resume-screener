from typing import List, Optional
from sqlalchemy.orm import Session
from app.job.repositories.job import job_repo
from app.job.models.job import Job
from app.job.schemas.job import JobCreate, JobUpdate, JobStatusUpdate, JobTagsUpdate, HiringTeamUpdate
from app.job.services.timeline_service import timeline_service

class JobService:
    def create_job(self, db: Session, job_in: JobCreate, user_id: Optional[str] = None) -> Job:
        obj_in = {
            "title": job_in.title,
            "department": job_in.department,
            "employment_type": job_in.employment_type,
            "location": job_in.location,
            "salary_range": job_in.salary_range,
            "custom_fields": job_in.custom_fields or {},
            "tags": job_in.tags or []
        }
            
        job = job_repo.create(db, obj_in)
        
        timeline_service.log_event(
            db=db,
            job_id=job.id,
            event_type="job_created",
            details={"title": job.title, "department": job.department},
            user_id=user_id
        )
        return job

    def get_job(self, db: Session, job_id: str) -> Optional[Job]:
        return job_repo.get(db, job_id)

    def update_job(self, db: Session, job_id: str, job_in: JobUpdate, user_id: Optional[str] = None) -> Optional[Job]:
        job = job_repo.get(db, job_id)
        if not job:
            return None
            
        obj_in = job_in.model_dump(exclude_unset=True)
        if not obj_in:
            return job
            
        updated_job = job_repo.update(db, job, obj_in)
        
        timeline_service.log_event(
            db=db,
            job_id=job.id,
            event_type="job_updated",
            details={"fields_updated": list(obj_in.keys())},
            user_id=user_id
        )
        return updated_job

    def update_status(self, db: Session, job_id: str, status_update: JobStatusUpdate, user_id: Optional[str] = None) -> Optional[Job]:
        job = job_repo.get(db, job_id)
        if not job:
            return None
            
        old_status = job.status
        new_status = status_update.status
        
        if old_status != new_status:
            job = job_repo.update(db, job, {"status": new_status})
            
            timeline_service.log_event(
                db=db,
                job_id=job.id,
                event_type="status_changed",
                details={"old_status": old_status, "new_status": new_status, "reason": status_update.reason},
                user_id=user_id
            )
        return job

    def update_tags(self, db: Session, job_id: str, tags_update: JobTagsUpdate, user_id: Optional[str] = None) -> Optional[Job]:
        job = job_repo.get(db, job_id)
        if not job:
            return None
            
        old_tags = job.tags or []
        new_tags = tags_update.tags
        
        if old_tags != new_tags:
            job = job_repo.update(db, job, {"tags": new_tags})
            
            timeline_service.log_event(
                db=db,
                job_id=job.id,
                event_type="tags_updated",
                details={"old_tags": old_tags, "new_tags": new_tags},
                user_id=user_id
            )
        return job

    def update_hiring_team(self, db: Session, job_id: str, team_update: HiringTeamUpdate, user_id: Optional[str] = None) -> Optional[Job]:
        job = job_repo.get(db, job_id)
        if not job:
            return None
            
        job = job_repo.update(db, job, {"hiring_team": team_update.hiring_team})
        
        timeline_service.log_event(
            db=db,
            job_id=job.id,
            event_type="hiring_team_updated",
            details={"new_team": team_update.hiring_team},
            user_id=user_id
        )
        return job

job_service = JobService()
