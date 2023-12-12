from transformers import pipeline
import torch

from dosaku import Module


class BARTSummarizer(Module):
    """Meta's BART model set up for summarization.

    Refer to the `paper <https://arxiv.org/abs/1910.13461>`_ for model details.
    """
    name = 'BARTSummarizer'

    def __init__(self, device='cuda'):
        super().__init__()
        self.model = None
        self.to(device)

    def to(self, device: str):
        self.remove_from_device()
        self.model = pipeline(
            "summarization",
            model="facebook/bart-large-cnn",
            device=device)

    def remove_from_device(self):
        if self.model is not None:
            del self.model
            torch.cuda.empty_cache()
        self.model = None

    def summarize(self, text: str, min_length: int = 30, max_length: int = 130, do_sample: bool = False) -> str:
        return self.model(text, min_length=min_length, max_length=max_length, do_sample=do_sample)[0]['summary_text']

    def __call__(self, *args, **kwargs) -> str:
        return self.summarize(*args, **kwargs)
