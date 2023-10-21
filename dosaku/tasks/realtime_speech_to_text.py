"""Interface for a Speech-to-Text task."""
from abc import abstractmethod

from dosaku import Task


class RealtimeSpeechToText(Task):
    """Abstract interface class for a realtime speech-to-text task."""
    name = 'RealtimeSpeechToText'

    @abstractmethod
    def stream(self, stream, new_chunk, **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    def reset_stream(self):
        raise NotImplementedError

    @abstractmethod
    def text(self):
        raise NotImplementedError


RealtimeSpeechToText.register_task()
