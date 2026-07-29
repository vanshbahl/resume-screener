from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.parsers.core.version import PARSER_VERSION, SCHEMA_VERSION


class SourceInfo(BaseModel):
    page: int
    section: str
    line: int


class EntityEvidence(BaseModel):
    detectors: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    original_values: List[str] = Field(default_factory=list)
    normalized_from: Optional[str] = None
    merge_reason: Optional[str] = None


class ExtractedField(BaseModel):
    value: Any
    confidence: float = 0.0
    evidence: Optional[EntityEvidence] = None
    source: Optional[SourceInfo] = None
    origin_model: str = "deterministic"


class PersonalInfo(BaseModel):
    name: Optional[ExtractedField] = None
    email: Optional[ExtractedField] = None
    phone: Optional[ExtractedField] = None
    linkedin: Optional[ExtractedField] = None
    github: Optional[ExtractedField] = None
    portfolio: Optional[ExtractedField] = None
    website: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None


class ExperienceEntry(BaseModel):
    company: Optional[ExtractedField] = None
    title: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None
    employment_type: Optional[ExtractedField] = None
    start_date: Optional[ExtractedField] = None
    end_date: Optional[ExtractedField] = None
    duration: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    skills_used: List[ExtractedField] = Field(default_factory=list)
    responsibilities: List[ExtractedField] = Field(default_factory=list)
    confidence: float = 0.0


class EducationEntry(BaseModel):
    institution: Optional[ExtractedField] = None
    degree: Optional[ExtractedField] = None
    field_of_study: Optional[ExtractedField] = None
    cgpa: Optional[ExtractedField] = None
    percentage: Optional[ExtractedField] = None
    start_date: Optional[ExtractedField] = None
    end_date: Optional[ExtractedField] = None
    graduation_year: Optional[ExtractedField] = None
    expected_graduation: Optional[ExtractedField] = None
    current_semester: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0


class ProjectEntry(BaseModel):
    name: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    technologies: List[ExtractedField] = Field(default_factory=list)
    link: Optional[ExtractedField] = None
    duration: Optional[ExtractedField] = None
    role: Optional[ExtractedField] = None
    awards: List[ExtractedField] = Field(default_factory=list)
    confidence: float = 0.0


class CertificationEntry(BaseModel):
    name: Optional[ExtractedField] = None
    issuer: Optional[ExtractedField] = None
    date: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0


class AchievementEntry(BaseModel):
    competition: Optional[ExtractedField] = None
    award: Optional[ExtractedField] = None
    rank: Optional[ExtractedField] = None
    position: Optional[ExtractedField] = None
    organizer: Optional[ExtractedField] = None
    year: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0


class SpokenLanguageEntry(BaseModel):
    name: ExtractedField
    fluency: Optional[ExtractedField] = None
    confidence: float = 0.0


class GenericActivityEntry(BaseModel):
    """Shared schema for Leadership, Volunteer Work, and Activities.

    A single reusable model for three structurally identical entity types.
    The originating section (leadership / volunteer / activities) is recorded
    via the source.section field on each ExtractedField.
    """

    organization: Optional[ExtractedField] = None
    role: Optional[ExtractedField] = None
    cause: Optional[ExtractedField] = None  # semantic hint for volunteer entries
    start_date: Optional[ExtractedField] = None
    end_date: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0


class PublicationEntry(BaseModel):
    """Flexible schema for academic and professional publications.

    All fields are Optional because publication formats on resumes are
    highly inconsistent (APA, MLA, informal one-liners). Capture whatever
    can be deterministically parsed; the rest is left for the AI layer.
    """

    title: Optional[ExtractedField] = None
    authors: List[ExtractedField] = Field(default_factory=list)
    venue: Optional[ExtractedField] = None  # journal, conference, book, or preprint server
    year: Optional[ExtractedField] = None
    doi: Optional[ExtractedField] = None
    url: Optional[ExtractedField] = None
    description: Optional[ExtractedField] = None
    confidence: float = 0.0


class Metadata(BaseModel):
    parser_version: str = PARSER_VERSION
    schema_version: str = SCHEMA_VERSION
    parsed_at: str
    processing_time_ms: int = 0
    ai_inference_time_ms: int = 0
    page_count: int = 0
    word_count: int = 0
    sections_detected: List[str] = Field(default_factory=list)
    entities_detected: int = 0
    entities_added_by_ai: int = 0
    entities_modified_by_ai: int = 0

    # Quality Metrics
    parser_confidence: float = 0.0
    extraction_coverage: float = 0.0
    normalization_coverage: float = 0.0
    validation_score: float = 100.0
    entity_quality_score: float = 0.0

    # Pipeline traceability
    ocr_triggered: bool = False
    feature_flags_active: List[str] = Field(default_factory=list)

    model_versions: Dict[str, str] = Field(default_factory=dict)
    resume_id: Optional[int] = None
    job_id: Optional[int] = None


class ParsedResumeSchema(BaseModel):
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: Optional[ExtractedField] = None
    skills: List[ExtractedField] = Field(default_factory=list)
    languages: List[ExtractedField] = Field(default_factory=list)
    spoken_languages: List[SpokenLanguageEntry] = Field(default_factory=list)
    frameworks: List[ExtractedField] = Field(default_factory=list)
    tools: List[ExtractedField] = Field(default_factory=list)
    concepts: List[ExtractedField] = Field(default_factory=list)
    soft_skills: List[ExtractedField] = Field(default_factory=list)
    education: List[EducationEntry] = Field(default_factory=list)
    experience: List[ExperienceEntry] = Field(default_factory=list)
    projects: List[ProjectEntry] = Field(default_factory=list)
    certifications: List[CertificationEntry] = Field(default_factory=list)
    achievements: List[AchievementEntry] = Field(default_factory=list)
    # Phase 1 new entity types
    leadership: List[GenericActivityEntry] = Field(default_factory=list)
    volunteer: List[GenericActivityEntry] = Field(default_factory=list)
    activities: List[GenericActivityEntry] = Field(default_factory=list)
    publications: List[PublicationEntry] = Field(default_factory=list)
    raw_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Metadata


def validate_and_score(parsed_dict: dict) -> dict:
    schema = ParsedResumeSchema(**parsed_dict)
    return schema.model_dump()
