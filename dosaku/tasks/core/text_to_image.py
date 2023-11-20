"""Interface for a Text-to-Image task."""
from abc import abstractmethod
from PIL.Image import Image

from dosaku import Task


class TextToImage(Task):
    """Abstract interface class for text-to-image task."""
    name = 'TextToImage'

    @abstractmethod
    def text_to_image(self, prompt: str, **kwargs) -> Image:
        """Generate an image given a prompt.

        Args:
            prompt: A text prompt describing the image to create.

        Returns:
            A PIL image.

        Example::

            from dosaku import agent

            agent = Agent()
            agent.learn('TextToImage')

            image = agent.TextToImage.text_to_image(prompt='An astronaut riding a horse; photographic 8k, f/1.4')
            image.show()

        """
        raise NotImplementedError

    @abstractmethod
    def __call__(self, prompt: str, **kwargs) -> Image:
        return self.text_to_image(prompt, **kwargs)


TextToImage.register_task()
