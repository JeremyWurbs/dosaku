from typing import List

from transformers import pipeline
import torch

from dosaku import Module
from dosaku.types import TextClassification


class BARTZeroShotClassifier(Module):
    """Meta's BART model set up for zero shot classification.

    Refer to the `paper <https://arxiv.org/abs/1909.00161>`_ for model details.
    """
    name = 'BARTZeroShotClassifier'

    def __init__(self, device='cuda'):
        super().__init__()
        self.model = None
        self.to(device)

    def to(self, device):
        self.remove_from_device()
        self.model = pipeline(
            'zero-shot-classification',
            model='facebook/bart-large-mnli',
            device=device)

    def remove_from_device(self):
        if self.model is not None:
            del self.model
            torch.cuda.empty_cache()
        self.model = None

    def classify(self, text: str, labels: List[str]) -> TextClassification:
        response = self.model(text, labels, multi_label=False)
        return TextClassification(
            classification=response['labels'][0],
            labels=response['labels'],
            scores=response['scores']
        )

    def __call__(self, text: str, labels: List[str]) -> TextClassification:
        return self.classify(text=text, labels=labels)
