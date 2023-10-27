from typing import List, Optional

from dosaku import Module
from dosaku.modules import OpenAIZeroShotTextClassification
from dosaku.utils import ifnone


class ZeroShotTextEvaluator(Module):
    name = 'ZeroShotTextEvaluator'

    def __init__(self, model: Optional[Module] = None):
        self.model = ifnone(model, default=OpenAIZeroShotTextClassification())

    def evaluate(self, text: str, labels: List[str]) -> str:
        return self.model(text=text, labels=labels).classification

    def classify(self, text: str, labels: List[str]) -> str:
        return self.evaluate(text=text, labels=labels)

    def __call__(self, text: str, labels: List[str]) -> str:
        return self.evaluate(text=text, labels=labels)


ZeroShotTextEvaluator.register_task('TextEvaluator')
ZeroShotTextEvaluator.register_task('ZeroShotTextClassification')