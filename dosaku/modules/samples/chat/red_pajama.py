from typing import List, Optional

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, StoppingCriteria, StoppingCriteriaList, TextIteratorStreamer

from dosaku import Module

device = 'cpu'


class RedPajama(Module):
    name = 'RedPajama'

    def __init__(self, device='cuda'):
        super().__init__()
        self.tokenizer = AutoTokenizer.from_pretrained("togethercomputer/RedPajama-INCITE-Chat-3B-v1")
        self.model = AutoModelForCausalLM.from_pretrained(
            "togethercomputer/RedPajama-INCITE-Chat-3B-v1",
            torch_dtype=torch.float16
        ).to(device)

    def message(self, message: str) -> str:
        raise NotImplementedError('I have lied. I have not implemented this method.')

    def __call__(self, *args, **kwargs):
        return self.message(*args, **kwargs)

    def predict(
            self,
            message: str,
            history: List[List[str]],
            system_prompt: Optional[str] = None,
            tokens: int = 100
    ) -> str:
        raise NotImplementedError('I have lied. I have not implemented this method.')


RedPajama.register_task(task='Chat')
RedPajama.register_task(task='GradioChat')
