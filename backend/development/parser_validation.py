import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.parsers.core.document import ResumeDocument
from app.main import get_default_pipeline

def validate_parser():
    sample_dir = "development/sample_resumes"
    pdfs = [f for f in os.listdir(sample_dir) if f.endswith(".pdf")] if os.path.exists(sample_dir) else []
    
    if not pdfs:
        print(f"No PDFs found in {sample_dir}.")
        print("Testing with a mock text payload instead...\n")
        mock_text = """
        John Doe
        johndoe@email.com | (555) 123-4567 | github.com/johndoe
        
        Summary
        A passionate software engineer with 5 years of experience.
        
        Skills
        Python, FastAPI, PostgreSQL, React
        
        Experience
        Software Engineer
        Acme Corp
        2020 - Present
        - Built a cool API
        - Scaled to 1M users
        
        Education
        B.S. Computer Science
        University of Technology
        2015 - 2019
        """
        
        mock_lines = []
        for i, line in enumerate(mock_text.split('\n')):
            if line.strip():
                mock_lines.append({"text": line.strip(), "page": 1, "line_no": i})
            
        doc = ResumeDocument(file_path="MOCK_TEXT")
        doc.raw_lines = mock_lines
        doc.metadata["page_count"] = 1
        doc.metadata["word_count"] = len(mock_text.split())
        
        pipeline = get_default_pipeline()
        doc = pipeline.run(doc)
        
        print(json.dumps(doc.final_json, indent=2))
        return

    for pdf in pdfs:
        path = os.path.join(sample_dir, pdf)
        print(f"Parsing {pdf}...")
        
        doc = ResumeDocument(file_path=path)
        pipeline = get_default_pipeline()
        doc = pipeline.run(doc)
        
        print(json.dumps(doc.final_json, indent=2))
        print("="*40)

if __name__ == "__main__":
    validate_parser()
