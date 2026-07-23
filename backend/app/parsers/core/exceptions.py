from dataclasses import dataclass
from typing import Optional

class ParserFatalError(Exception):
    """Raised when the document cannot be processed further."""
    pass

class ParserRecoverableError(Exception):
    """Raised when a specific stage fails but pipeline can continue."""
    pass

@dataclass
class ParserWarning:
    type: str
    message: str
    stage: str
    line_no: Optional[int] = None
