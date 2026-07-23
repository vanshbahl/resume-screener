import fitz
from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import BaseDocument, PipelineContext
from app.parsers.core.exceptions import ParserFatalError

class PDFExtractionStage(BaseParserStage):
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        if document.raw_lines: 
            return # Skip if populated manually by tests
            
        lines = []
        word_count = 0
        line_index = 0
        
        try:
            if document.file_path.endswith('.txt'):
                with open(document.file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                page_count = 1
                for line in text.split('\n'):
                    cleaned_line = line.strip()
                    if cleaned_line:
                        lines.append({
                            "text": cleaned_line,
                            "page": 1,
                            "line_no": line_index
                        })
                        word_count += len(cleaned_line.split())
                    line_index += 1
            else:
                doc = fitz.open(document.file_path)
                page_count = len(doc)
                
                for page_num, page in enumerate(doc, start=1):
                    text = page.get_text()
                    page_lines = text.split('\n')
                    
                    for line in page_lines:
                        cleaned_line = line.strip()
                        if cleaned_line:
                            lines.append({
                                "text": cleaned_line,
                                "page": page_num,
                                "line_no": line_index
                            })
                            word_count += len(cleaned_line.split())
                        line_index += 1  # Always increment — blank lines create gaps in line_no for block-splitting
            
            if page_count == 0 or len(lines) == 0:
                context.log_warning("EmptyResume", "No text could be extracted from PDF.")
                
            document.raw_lines = lines
            document.metadata["page_count"] = page_count
            document.metadata["word_count"] = word_count
        except Exception as e:
            raise ParserFatalError(f"PDF Extraction failed: {e}")
