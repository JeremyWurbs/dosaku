"""Interface for a Text-to-Image task."""
from abc import abstractmethod
from PIL.Image import Image

from dosaku import Task


class TextToImage(Task):
    """Abstract interface class for text-to-image task."""
    name = 'TextToImage'

    @abstractmethod
    def text_to_image(self, prompt: str, **kwargs) -> Image:
        raise NotImplementedError


TextToImage.register_task()
