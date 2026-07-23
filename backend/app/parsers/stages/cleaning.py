import re

from app.parsers.core.base import BaseParserStage
from app.parsers.core.document import BaseDocument, PipelineContext


class TextCleaningStage(BaseParserStage):
    def run(self, document: BaseDocument, context: PipelineContext) -> None:
        cleaned_lines = []

        for line_obj in document.raw_lines:
            text = line_obj["text"]

            text = text.replace("\u200b", "")
            text = text.replace("\xa0", " ")
            text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")

            text = re.sub(r"\s+", " ", text).strip()

            if text:
                cleaned_lines.append(
                    {
                        "text": text,
                        "page": line_obj["page"],
                        "line_no": line_obj["line_no"],
                    }
                )

        if not cleaned_lines and document.raw_lines:
            context.log_warning(
                "OCRNoiseDetected", "All lines were stripped during cleaning."
            )

        document.cleaned_lines = cleaned_lines
