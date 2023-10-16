from abc import abstractmethod
from dataclasses import dataclass
from PIL.Image import Image
from typing import List, Optional

from dosaku import Task


class RestoreFaces(Task):
    """Interface for a generic module that can restore faces in images."""
    name = 'RestoreFaces'

    @dataclass
    class RestoredImage:
        restored_image: Image
        cropped_faces: Optional[List[Image]] = None
        restored_faces: Optional[List[Image]] = None

    def __init__(self):
        super().__init__()

    @abstractmethod
    def restore(self, image: Image, **kwargs) -> RestoredImage:
        """Restore faces in given image.

        Args:
            image: The input image. It may contain one or more disfigured or low-quality faces.

        Returns:
            A RestoreFaces.RestoredImage object containing, at minimum, the restored_image. Individual modules may also
            provide the individual cropped faces, both before and after correcting, if able, but are not obligated to
            do so.

        Example::

            from PIL import Image
            from dosaku import Agent
            from dosaku.utils import draw_images

            agent = Agent()
            agent.learn('RestoreFaces')

            image = Image.open('tests/resources/hopper_photograph.png')
            restoration = agent.RestoreFaces.restore(image)

            draw_images((image, restoration.restored_image), labels=('Original', 'Restored Image'))
        """
        raise NotImplementedError


RestoreFaces.register_task()
