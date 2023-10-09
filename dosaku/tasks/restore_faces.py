from abc import abstractmethod
from dataclasses import dataclass
from PIL.Image import Image
from typing import List, Optional

from dosaku import Task


@dataclass
class RestoredImage:
    restored_image: Image
    cropped_faces: Optional[List[Image]] = None
    restored_faces: Optional[List[Image]] = None


class RestoreFaces(Task):
    """Interface for a generic module that can restore faces in images."""
    name = 'RestoreFaces'

    def __init__(self):
        super().__init__()

    @abstractmethod
    def restore(self, image: Image, **kwargs) -> RestoredImage:
        """Restore faces in given image.

        Args:
            message: The message to send the chat agent.

        Returns:
            A RestoredImage object containing, at minimum, the restored_image. Individual modules may also provide the
            individual cropped faces, both before and after correcting, if able.

        Example::

            from PIL import Image
            from dosaku import Agent

            image = Image.open('tests/resources/disfigured_face.png')

            agent = Agent()
            agent.learn('RestoreFaces')
            restoration = agent.RestoreFaces(image)
            restoration.restored_image.show()
        """
        raise NotImplementedError


RestoreFaces.register_task()
