"""Interface for a Zero Shot Text Classification task."""
from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from dosaku import Task


class ZeroShotTextClassification(Task):
    """Abstract interface class for zero-shot text classification task."""
    name = 'ZeroShotTextClassification'

    @dataclass
    class TextClassification:
        classification: str
        labels: Optional[List[str]] = None
        scores: Optional[List[float]] = None

    @abstractmethod
    def classify(self, text: str, labels: List[str], **kwargs) -> TextClassification:
        """Classify the text as belonging to one of the given classes."""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, text: str, labels: List[str], **kwargs) -> TextClassification:
        return self.classify(text, labels=labels, **kwargs)


ZeroShotTextClassification.register_task()
