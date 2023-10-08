# Reference sample for creating a Module and registering it to a pre-existing Task.

from typing import List, Optional

from dosaku import Module


class EchoBot(Module):
    name = 'EchoBot'

    def __init__(self):
        super().__init__()

    def chat(self, message: str) -> str:
        return f'Hi, I\'m EchoBot.'

    def predict(
            self,
            message: str,
            history: List[List[str]],
            system_prompt: Optional[str] = None,
            tokens: int = 100
    ) -> str:
        response = f"Hello {message}! I\'m EchoBot."
        return response[: min(len(response), tokens)]


EchoBot.register_task(task='Chat')
EchoBot.register_task(task='GradioChat')
