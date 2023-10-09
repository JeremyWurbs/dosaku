from abc import abstractmethod
from PIL.Image import Image
from typing import Any

from dosaku import Task


class ObjectDetection(Task):
    """Interface for a generic object detection module."""
    name = 'ObjectDetection'

    def __init__(self):
        super().__init__()

    @abstractmethod
    def detect(self, image: Image, **kwargs) -> Any:
        """Object detection.

        Args:
            image: An input image.

        Returns:
            The detected objects. The exact return type will differ by module implementation.
        """

    @classmethod
    @abstractmethod
    def __call__(cls, image: Image, **kwargs) -> Any:
        """Utility method to call detect()."""
        raise NotImplementedError


ObjectDetection.register_task()
