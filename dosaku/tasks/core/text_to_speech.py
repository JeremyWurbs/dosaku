"""Interface for a Text-to-Image task."""
from abc import abstractmethod

from dosaku import Task
from dosaku.types import Audio


class TextToSpeech(Task):
    """Abstract interface class for text-to-speech task."""
    name = 'TextToImage'

    @abstractmethod
    def text_to_speech(self, text: str, **kwargs) -> Audio:
        """Return speech audio from the given text.

        Args:
            text: The text to turn into speech audio.

        Returns:
            A dosaku Audio object with the associated speech audio.

        """
        raise NotImplementedError
