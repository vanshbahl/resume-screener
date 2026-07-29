from typing import List

from fastapi import (APIRouter, BackgroundTasks, Depends, File, HTTPException,
                     UploadFile)
from sqlalchemy.orm import Session

from app.candidate.repositories.candidate import candidate_repo, resume_repo
from app.candidate.schemas.candidate import (CandidateCreate,
                                             CandidateNoteCreate,
                                             CandidateNoteResponse,
                                             CandidateResponse,
                                             CandidateResumeDetailResponse,
                                             CandidateResumeResponse,
                                             CandidateStatusUpdate,
                                             CandidateTagsUpdate,
                                             CandidateTimelineResponse,
                                             CandidateUpdate)
from app.candidate.services.candidate_service import candidate_service
from app.candidate.services.note_service import note_service
from app.candidate.services.resume_service import resume_service
from app.candidate.services.timeline_service import timeline_service
from app.core.database import get_db
from app.parsers.pdf_validator import PDFValidationError

router = APIRouter(prefix="/candidates", tags=["Candidate Management"])


@router.post("/", response_model=CandidateResponse)
def create_candidate(candidate_in: CandidateCreate, db: Session = Depends(get_db)):
    return candidate_service.create_candidate(db, candidate_in)


@router.get("/", response_model=List[CandidateResponse])
def get_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return candidate_repo.get_multi(db, skip=skip, limit=limit)


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)):
    candidate = candidate_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.patch("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: str, candidate_in: CandidateUpdate, db: Session = Depends(get_db)
):
    candidate = candidate_service.update_candidate(db, candidate_id, candidate_in)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/{candidate_id}/status", response_model=CandidateResponse)
def update_status(
    candidate_id: str,
    status_update: CandidateStatusUpdate,
    db: Session = Depends(get_db),
):
    candidate = candidate_service.update_status(db, candidate_id, status_update)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.post("/{candidate_id}/tags", response_model=CandidateResponse)
def update_tags(
    candidate_id: str, tags_update: CandidateTagsUpdate, db: Session = Depends(get_db)
):
    candidate = candidate_service.update_tags(db, candidate_id, tags_update)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


# --- Resumes ---
@router.post("/{candidate_id}/resume", response_model=CandidateResumeResponse)
async def upload_resume(
    candidate_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    file_bytes = await file.read()
    try:
        resume = resume_service.upload_resume(
            db, candidate_id, file_bytes, file.filename, file.content_type
        )
        # Background task for parsing — runs after the response is returned.
        background_tasks.add_task(
            resume_service.process_resume, next(get_db()), resume.id
        )
        return resume
    except PDFValidationError as e:
        raise HTTPException(status_code=400, detail=e.detail)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{candidate_id}/resume/{resume_id}",
    response_model=CandidateResumeDetailResponse,
)
def get_resume_detail(
    candidate_id: str, resume_id: str, db: Session = Depends(get_db)
):
    resume = resume_repo.get(db, resume_id)
    if not resume or resume.candidate_id != candidate_id:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


# --- Timeline ---
@router.get("/{candidate_id}/timeline", response_model=List[CandidateTimelineResponse])
def get_timeline(candidate_id: str, db: Session = Depends(get_db)):
    return timeline_service.get_candidate_timeline(db, candidate_id)


# --- Notes ---
@router.post("/{candidate_id}/notes", response_model=CandidateNoteResponse)
def add_note(
    candidate_id: str, note_in: CandidateNoteCreate, db: Session = Depends(get_db)
):
    candidate = candidate_service.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return note_service.add_note(
        db, candidate_id, note_in, author="Current User"
    )  # Hardcoded author for now
