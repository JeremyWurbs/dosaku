"""Interface for a Speech-to-Text task."""
from abc import abstractmethod

from dosaku import Task


class SpeechToText(Task):
    """Abstract interface class for a speech-to-text task."""
    name = 'SpeechToText'

    @abstractmethod
    def transcribe(self, audio, **kwargs) -> str:
        raise NotImplementedError


SpeechToText.register_task()
