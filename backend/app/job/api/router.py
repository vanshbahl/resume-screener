from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.job.schemas.job import (
    JobCreate, JobUpdate, JobResponse,
    JobStatusUpdate, JobTagsUpdate, HiringTeamUpdate,
    JobDescriptionResponse, JobTimelineResponse,
    JobNoteCreate, JobNoteResponse
)
from app.job.services.job_service import job_service
from app.job.services.job_description_service import job_description_service
from app.job.services.timeline_service import timeline_service
from app.job.services.note_service import note_service
from app.job.repositories.job import job_repo

router = APIRouter(prefix="/jobs", tags=["Job Management"])

@router.post("/", response_model=JobResponse)
def create_job(job_in: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, job_in)

@router.get("/", response_model=List[JobResponse])
def get_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return job_repo.get_multi(db, skip=skip, limit=limit)

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.patch("/{job_id}", response_model=JobResponse)
def update_job(job_id: str, job_in: JobUpdate, db: Session = Depends(get_db)):
    job = job_service.update_job(db, job_id, job_in)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/status", response_model=JobResponse)
def update_status(job_id: str, status_update: JobStatusUpdate, db: Session = Depends(get_db)):
    job = job_service.update_status(db, job_id, status_update)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/tags", response_model=JobResponse)
def update_tags(job_id: str, tags_update: JobTagsUpdate, db: Session = Depends(get_db)):
    job = job_service.update_tags(db, job_id, tags_update)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.post("/{job_id}/hiring-team", response_model=JobResponse)
def update_hiring_team(job_id: str, team_update: HiringTeamUpdate, db: Session = Depends(get_db)):
    job = job_service.update_hiring_team(db, job_id, team_update)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

# --- Job Descriptions ---
@router.post("/{job_id}/description", response_model=JobDescriptionResponse)
async def upload_job_description(
    job_id: str, 
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    file_bytes = await file.read()
    try:
        jd = job_description_service.upload_description(db, job_id, file_bytes, file.filename, file.content_type)
        # Background task for parsing
        background_tasks.add_task(job_description_service.process_description, next(get_db()), jd.id)
        return jd
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Timeline ---
@router.get("/{job_id}/timeline", response_model=List[JobTimelineResponse])
def get_timeline(job_id: str, db: Session = Depends(get_db)):
    return timeline_service.get_job_timeline(db, job_id)

# --- Notes ---
@router.post("/{job_id}/notes", response_model=JobNoteResponse)
def add_note(job_id: str, note_in: JobNoteCreate, db: Session = Depends(get_db)):
    job = job_service.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return note_service.add_note(db, job_id, note_in, author="Current User") # Hardcoded author for now
