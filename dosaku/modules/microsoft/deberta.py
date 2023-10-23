from typing import List

from transformers import pipeline

from dosaku import Module
from dosaku.tasks import ZeroShotTextClassification


class DeBERTa(Module):
    """Microsoft's DeBERTa model.

    Refer to the `paper <https://arxiv.org/pdf/2006.03654.pdf>`_ for model details.
    """
    name = 'DeBERTa'

    def __init__(self, device='cuda'):
        super().__init__()

        self.model = pipeline(
            'zero-shot-classification',
            model='MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli',
            device=device)

    def classify(self, text: str, labels: List[str]) -> ZeroShotTextClassification.TextClassification:
        response = self.model(text, labels, multi_label=False)
        return ZeroShotTextClassification.TextClassification(
            classification=response['labels'][0],
            labels=response['labels'],
            scores=response['scores']
        )


    def __call__(self, text: str, labels: List[str]) -> ZeroShotTextClassification.TextClassification:
        return self.classify(text=text, labels=labels)


DeBERTa.register_task('ZeroShotTextClassification')
