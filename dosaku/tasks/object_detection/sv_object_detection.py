from abc import abstractmethod
from PIL.Image import Image

import supervision as sv

from dosaku import Task


class ObjectDetectionSV(Task):
    """Interface for an object detection module that returns Supervision detections."""
    name = 'ObjectDetectionSV'

    def __init__(self):
        super().__init__()

    @abstractmethod
    def detect(self, image: Image, **kwargs) -> sv.Detections:
        """Object detection.

        Args:
            image: An input image.

        Returns:
            A sv.Detections object containing the found detections.
        """

    @classmethod
    @abstractmethod
    def __call__(cls, image: Image, **kwargs) -> sv.Detections:
        """Utility method to call detect()."""
        raise NotImplementedError


ObjectDetectionSV.register_task()
