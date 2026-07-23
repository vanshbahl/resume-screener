import logging
from contextlib import asynccontextmanager

from fastapi import (FastAPI, Request, status)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.decision import router as decision_router
from app.api.intelligence import router as intelligence_router
from app.api.search import router as search_router
from app.candidate.api.router import router as candidate_router
from app.core.config import settings
from app.core.database import Base, engine
from app.job.api.router import router as job_router
from app.parsers.pipeline import ParserPipeline
from app.parsers.stages.cleaning import TextCleaningStage
from app.parsers.stages.entity_extraction import EntityExtractionStage
from app.parsers.stages.entity_fusion import EntityFusionStage
from app.parsers.stages.extraction import PDFExtractionStage
from app.parsers.stages.hf_ner import HuggingFaceNERStage
from app.parsers.stages.normalization import NormalizationStage
from app.parsers.stages.section_detection import SectionDetectionStage
from app.parsers.stages.spacy_ner import SpacyNERStage
from app.parsers.stages.validation import ValidationStage
from app.workflow.api.router import router as workflow_router
from app.workspace.api.router import router as workspace_router
from app.interview.api.router import router as interview_router
from app.analytics.api.router import router as analytics_router
from app.identity.api.router import router as identity_router


def get_default_pipeline() -> ParserPipeline:
    return ParserPipeline(
        [
            PDFExtractionStage(),
            TextCleaningStage(),
            SectionDetectionStage(),
            EntityExtractionStage(),
            SpacyNERStage(),
            HuggingFaceNERStage(),
            EntityFusionStage(),
            NormalizationStage(),
            ValidationStage(),
        ]
    )


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up... Creating database tables if they do not exist.")
    try:
        import app.models.domain # Ensure all models are registered
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Centralized Exception Handlers
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error occurred: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "A database error occurred while processing the request."},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred."},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )


@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(intelligence_router)
app.include_router(search_router)
app.include_router(decision_router)
app.include_router(candidate_router)
app.include_router(job_router)
app.include_router(workflow_router)
app.include_router(workspace_router)
app.include_router(interview_router)
app.include_router(analytics_router)
app.include_router(identity_router)
