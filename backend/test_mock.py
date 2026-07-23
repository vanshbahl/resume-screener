import sys
import json
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.parsers.core.document import ResumeDocument
from app.main import get_default_pipeline

document = ResumeDocument(file_path="MOCK_TEXT")
mock_text = """
John Doe
Senior Software Engineer
johndoe@email.com | +1 (555) 123-4567 | San Francisco, CA
github.com/johndoe | linkedin.com/in/johndoe | myportfolio.com

SUMMARY
Highly motivated senior backend engineer with 5 years of experience building scalable microservices and APIs.

EXPERIENCE
Tech Innovations Inc.
Senior Software Engineer
January 2021 - Present
- Architected a distributed messaging queue handling 1M+ req/sec.
- Reduced latency by 40% using Redis and Golang.
- Developed REST APIs in FastAPI and Django.

Acme Corp
Software Engineer II
Feb 2018 - Dec 2020 (2 years 10 months)
- Built REST APIs in Django.
- Migrated monolith to Kubernetes and AWS.

EDUCATION
B.S. in Computer Science
University of Technology
Sep 2014 - May 2018
CGPA: 3.8/4.0
85%

PROJECTS
OpenSource Analytics
- Built a highly scalable analytics engine using Python and Postgres.
- https://github.com/johndoe/analytics
- Duration: 3 months
- Winner of the regional hackathon 2022

CERTIFICATIONS
AWS Certified Solutions Architect
Amazon Web Services
2021

ACHIEVEMENTS
1st Place in Global Coding Challenge
2020
Smart India Hackathon 2nd runner up

LANGUAGES
English (Native), Spanish (Fluent)

SKILLS
Languages: Python, Go, JavaScript, SQL, C++, HTML
Frameworks: FastAPI, ReactJS, Django
Databases: PostgreSQL, MongoDB, Redis
Tools: Docker, Kubernetes, AWS, Git
Soft Skills: Leadership, Excellent Communication
"""
document.raw_lines = [{"text": line.strip(), "page": 1, "line_no": i} for i, line in enumerate(mock_text.split('\n')) if line.strip()]
document.metadata["page_count"] = 1
document.metadata["word_count"] = len(mock_text.split())

pipeline = get_default_pipeline()
document = pipeline.run(document)
print(json.dumps(document.final_json, indent=2))
