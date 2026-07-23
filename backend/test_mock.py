import sys
import json
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.parsers.core.document import ResumeDocument
from app.parsers.pipeline import ParserPipeline
from app.parsers.stages.extraction import PDFExtractionStage
from app.parsers.stages.cleaning import TextCleaningStage
from app.parsers.stages.section_detection import SectionDetectionStage
from app.parsers.stages.entity_extraction import EntityExtractionStage
from app.parsers.stages.normalization import NormalizationStage
from app.parsers.stages.validation import ValidationStage

def get_default_pipeline() -> ParserPipeline:
    return ParserPipeline([
        PDFExtractionStage(), TextCleaningStage(), SectionDetectionStage(),
        EntityExtractionStage(), NormalizationStage(), ValidationStage()
    ])

document = ResumeDocument(file_path="MOCK_TEXT")
mock_text = """
John Doe
Software Engineer
johndoe@email.com | +1 (555) 123-4567 | San Francisco, CA
github.com/johndoe | linkedin.com/in/johndoe | myportfolio.com

SUMMARY
Highly motivated senior backend engineer with 5 years of experience building scalable microservices and APIs.

EXPERIENCE
Senior Software Engineer
Tech Innovations Inc.
January 2021 - Present
- Architected a distributed messaging queue handling 1M+ req/sec.
- Reduced latency by 40% using Redis and Golang.

Software Engineer II
Acme Corp
Feb 2018 - Dec 2020
- Built REST APIs in Django.
- Migrated monolith to Kubernetes.

EDUCATION
B.S. in Computer Science
University of Technology
Sep 2014 - May 2018
CGPA: 3.8/4.0

PROJECTS
OpenSource Analytics
- Built a highly scalable analytics engine.
- https://github.com/johndoe/analytics
- Duration: 3 months

SKILLS
Languages: Python, Go, JavaScript, SQL
Frameworks: FastAPI, React, Django
Databases: PostgreSQL, MongoDB, Redis
Tools: Docker, Kubernetes, AWS, Git
Soft Skills: Leadership, Communication
"""
document.raw_lines = [{"text": line.strip(), "page": 1, "line_no": i} for i, line in enumerate(mock_text.split('\n')) if line.strip()]
document.metadata["page_count"] = 1
document.metadata["word_count"] = len(mock_text.split())

pipeline = get_default_pipeline()
document = pipeline.run(document)
print(json.dumps(document.final_json, indent=2))
