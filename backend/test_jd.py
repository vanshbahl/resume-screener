import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.parsers.core.document import JobDocument
from app.main import get_default_pipeline
import json

doc = JobDocument(file_path='parser_tests/datasets/sample_jds/backend_engineer.txt')
pipe = get_default_pipeline()

doc = pipe.run(doc)
print(json.dumps(doc.final_json, indent=2))
