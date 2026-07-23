import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.parsers.core.document import ResumeDocument
from app.main import get_default_pipeline

doc = ResumeDocument(file_path='parser_tests/datasets/sample_resumes/backend_0_2_years_017.pdf')
pipe = get_default_pipeline()

try:
    doc = pipe.run(doc)
    print("Pipeline ran successfully.")
    print("Keys in final_json:", doc.final_json.keys())
except Exception as e:
    import traceback
    traceback.print_exc()

# Let's see if we can find recoverable errors inside the context if not bubbled up
# The pipeline doesn't expose context. So we can just run the stages manually.
from app.parsers.core.document import PipelineContext
context = PipelineContext()
for stage in pipe.stages:
    print(f"Running stage {stage.name}...")
    try:
        stage.run(doc, context)
    except Exception as e:
        import traceback
        print(f"Exception in {stage.name}:")
        traceback.print_exc()

print("Recoverable errors:")
print(context.recoverable_errors)
