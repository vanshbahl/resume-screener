import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.parsers.core.document import ResumeDocument
from app.main import get_default_pipeline

def run_benchmark():
    sample_dir = "development/sample_resumes"
    results_file = "development/benchmark_results.json"
    
    if not os.path.exists(sample_dir):
        print(f"Directory {sample_dir} not found.")
        return
        
    pdfs = [f for f in os.listdir(sample_dir) if f.endswith(".pdf")]
    
    metrics = {
        "total_resumes": 0,
        "total_processing_time_ms": 0,
        "average_processing_time_ms": 0,
        "average_confidence": 0,
        "extraction_rates": {
            "name": 0,
            "email": 0,
            "phone": 0,
            "education": 0,
            "experience": 0,
            "skills": 0
        },
        "ai_metrics": {
            "total_inference_time_ms": 0,
            "total_entities_added": 0,
            "total_entities_modified": 0
        },
        "failures": []
    }
    total_conf = 0.0
    total_resumes = 0
    
    if not pdfs:
        print("No PDFs found. Using dense mock payload.")
        pdfs = ["MOCK_TEXT"]
    
    for pdf in pdfs:
        path = os.path.join(sample_dir, pdf) if pdf != "MOCK_TEXT" else "MOCK_TEXT"
        try:
            document = ResumeDocument(file_path=path)
            
            if pdf == "MOCK_TEXT":
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
                mock_lines = []
                for i, line in enumerate(mock_text.split('\n')):
                    if line.strip():
                        mock_lines.append({"text": line.strip(), "page": 1, "line_no": i})
                document.raw_lines = mock_lines
                document.metadata["page_count"] = 1
                document.metadata["word_count"] = len(mock_text.split())
            
            pipeline = get_default_pipeline()
            document = pipeline.run(document)
            result = document.final_json
            
            md = result.get("metadata", {})
            metrics["total_processing_time_ms"] += md.get("processing_time_ms", 0)
            total_conf += md.get("parsing_confidence", 0.0)
            
            pi = result.get("personal_info", {})
            if pi.get("name") and pi["name"].get("value"): metrics["extraction_rates"]["name"] += 1
            if pi.get("email") and pi["email"].get("value"): metrics["extraction_rates"]["email"] += 1
            if pi.get("phone") and pi["phone"].get("value"): metrics["extraction_rates"]["phone"] += 1
            
            if result.get("education"): metrics["extraction_rates"]["education"] += 1
            if result.get("experience"): metrics["extraction_rates"]["experience"] += 1
            if result.get("skills"): metrics["extraction_rates"]["skills"] += 1
            
            # AI Tracking
            meta = result.get("metadata", {})
            metrics["ai_metrics"]["total_inference_time_ms"] += meta.get("ai_inference_time_ms", 0)
            metrics["ai_metrics"]["total_entities_added"] += meta.get("entities_added_by_ai", 0)
            metrics["ai_metrics"]["total_entities_modified"] += meta.get("entities_modified_by_ai", 0)
            
            total_resumes += 1
            
        except Exception as e:
            metrics["failures"].append({"file": pdf, "error": str(e)})

    metrics["total_resumes"] = total_resumes
    if total_resumes > 0:
        metrics["average_processing_time_ms"] = round(metrics["total_processing_time_ms"] / total_resumes, 2)
        metrics["average_confidence"] = round(total_conf / total_resumes, 2)
        
        metrics["ai_metrics"]["average_inference_time_ms"] = round(metrics["ai_metrics"]["total_inference_time_ms"] / total_resumes, 2)
        metrics["ai_metrics"]["average_entities_added"] = round(metrics["ai_metrics"]["total_entities_added"] / total_resumes, 2)
        metrics["ai_metrics"]["average_entities_modified"] = round(metrics["ai_metrics"]["total_entities_modified"] / total_resumes, 2)
        
        for k in metrics["extraction_rates"]:
            metrics["extraction_rates"][k] = round((metrics["extraction_rates"][k] / total_resumes) * 100, 2)
            
    with open(results_file, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Benchmarking complete. Results saved to {results_file}")

if __name__ == "__main__":
    run_benchmark()
