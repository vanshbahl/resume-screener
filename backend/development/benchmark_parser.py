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
        "total_resumes": len(pdfs),
        "total_processing_time_ms": 0,
        "average_processing_time_ms": 0,
        "average_confidence": 0.0,
        "extraction_rates": {
            "name": 0.0,
            "email": 0.0,
            "phone": 0.0,
            "education": 0.0,
            "experience": 0.0,
            "skills": 0.0
        },
        "failures": []
    }
    
    total_conf = 0.0
    
    if not pdfs:
        with open(results_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        print("Benchmarked 0 files.")
        return

    for pdf in pdfs:
        path = os.path.join(sample_dir, pdf)
        try:
            document = ResumeDocument(file_path=path)
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
            
        except Exception as e:
            metrics["failures"].append({"file": pdf, "error": str(e)})

    if metrics["total_resumes"] > 0:
        metrics["average_processing_time_ms"] = round(metrics["total_processing_time_ms"] / metrics["total_resumes"], 2)
        metrics["average_confidence"] = round(total_conf / metrics["total_resumes"], 2)
        
        for k in metrics["extraction_rates"]:
            metrics["extraction_rates"][k] = round((metrics["extraction_rates"][k] / metrics["total_resumes"]) * 100, 2)
            
    with open(results_file, 'w') as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Benchmarking complete. Results saved to {results_file}")

if __name__ == "__main__":
    run_benchmark()
