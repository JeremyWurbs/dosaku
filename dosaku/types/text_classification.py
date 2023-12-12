from dataclasses import dataclass
from typing import List, Optional


@dataclass
class TextClassification:
    classification: str
    labels: Optional[List[str]] = None
    scores: Optional[List[float]] = None
