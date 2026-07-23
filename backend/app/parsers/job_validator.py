from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.parsers.resume_validator import (ExtractedField,
                                          Metadata)


class JobMetadata(BaseModel):
    title: Optional[ExtractedField] = None
    company: Optional[ExtractedField] = None
    department: Optional[ExtractedField] = None
    job_id: Optional[ExtractedField] = None


class ParsedJobSchema(BaseModel):
    job_metadata: JobMetadata = Field(default_factory=JobMetadata)
    employment_type: Optional[ExtractedField] = None
    location: Optional[ExtractedField] = None
    industry: Optional[ExtractedField] = None
    salary: Optional[ExtractedField] = None
    experience_requirements: Optional[ExtractedField] = None
    education_requirements: List[ExtractedField] = Field(default_factory=list)

    responsibilities: List[ExtractedField] = Field(default_factory=list)
    qualifications: List[ExtractedField] = Field(default_factory=list)

    required_skills: List[ExtractedField] = Field(default_factory=list)
    preferred_skills: List[ExtractedField] = Field(default_factory=list)

    technologies: List[ExtractedField] = Field(default_factory=list)
    soft_skills: List[ExtractedField] = Field(default_factory=list)
    tools: List[ExtractedField] = Field(default_factory=list)
    frameworks: List[ExtractedField] = Field(default_factory=list)
    concepts: List[ExtractedField] = Field(default_factory=list)
    languages: List[ExtractedField] = Field(default_factory=list)
    certifications: List[ExtractedField] = Field(default_factory=list)

    benefits: List[ExtractedField] = Field(default_factory=list)
    keywords: List[ExtractedField] = Field(default_factory=list)

    raw_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Metadata


def validate_and_score_jd(parsed_dict: dict) -> dict:
    schema = ParsedJobSchema(**parsed_dict)
    return schema.model_dump()
