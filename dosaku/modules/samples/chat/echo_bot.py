# Reference sample for creating a Module and registering it to a pre-existing Task.

from typing import Generator, Union

from dosaku import Module


class EchoBot(Module):
    name = 'EchoBot'

    def __init__(self, stream=False):
        super().__init__()
        self.stream = stream

    def message(self, message: str, **_) -> Union[str, Generator[str, None, None]]:
        if self.stream:
            return self._message_stream(message)
        else:
            return self._message(message)

    def _message(self, message: str) -> str:
        return f'Hi, I\'m EchoBot. You said: \"{message}\".'

    def _message_stream(self, message: str) -> Generator[str, None, None]:
        response = self._message(message)
        for i in range(len(response)):
            yield response[:i]

    def __call__(self, *args, **kwargs):
        return self.message(*args, **kwargs)


EchoBot.register_task(task='Chat')
