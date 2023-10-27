from abc import abstractmethod
from typing import Any, List

from dosaku import Task


class TextEvaluator(Task):
    name = 'TextEvaluator'

    @abstractmethod
    def evaluate(self, text: str, labels: List[str]) -> str:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, text: str, labels: List[str]) -> str:
        return self.evaluate_text(text=text, labels=labels)


TextEvaluator.register_task()
