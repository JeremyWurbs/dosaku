from abc import abstractmethod
from PIL.Image import Image

import supervision as sv

from dosaku import Task


class SVObjectDetection(Task):
    """Interface for an object detection module return Supervision detections."""
    name = 'SVObjectDetection'

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


SVObjectDetection.register_task()
