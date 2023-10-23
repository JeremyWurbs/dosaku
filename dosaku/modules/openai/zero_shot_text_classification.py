from typing import List, Optional

from dosaku import Service
from dosaku.modules import OpenAIChat
from dosaku.tasks import ZeroShotTextClassification
from dosaku.utils import ifnone


class OpenAIZeroShotTextClassification(Service):
    """Zero Shot Text Classification using OpenAI's GPT API."""
    name = 'OpenAIZeroShotTextClassification'
    default_system_prompt = (
        'You are an AI tasked with determining how to classify a piece of conversational text. Given a piece of '
        'text and associated labels, you should return one label. The returned label should be the one that most '
        'closely describes the given text.\n'
        '\n'
        'For example,\n'
        '\n'
        'Classify the text: \"Sure, here is your code for a gcd method.\n'
        '\n'
        '```python'
        'def gcd(a, b):\n'
        '   while b != 0:\n'
        '       a, b = b, a % b\n'
        '   return a'
        '```'
        '\n'
        'The gcd method takes two integers and computes their greatest common denominator.\"\n'
        '\n'
        'As one of the following labels: [\'general chat\', \'code\', \'plan to complete task\']\n'
        '\n'
        'code'
    )

    def __init__(
            self,
            model: Optional[str] = None,
            system_prompt: Optional[str] = None,
            temperature: float = 0.1,
            **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.system_prompt = ifnone(system_prompt, default=self.default_system_prompt)
        self.temperature = temperature

    def classify(self, text: str, labels: List[str]) -> ZeroShotTextClassification.TextClassification:
        conversation = OpenAIChat(system_prompt=self.system_prompt, temperature=self.temperature)
        message = f'Classify the text: {text}\n\nAs one of the following labels: {labels}\n\n'
        classification = conversation.message(message=message)
        return ZeroShotTextClassification.TextClassification(
            classification=classification
        )

    def __call__(self, text: str, labels: List[str]) -> ZeroShotTextClassification.TextClassification:
        return self.classify(text=text, labels=labels)


OpenAIZeroShotTextClassification.register_task('ZeroShotTextClassification')
