"""Utility methods relating to image processing."""
from typing import List, Union
from PIL.Image import Image

from matplotlib.figure import Figure
import matplotlib.pyplot as plt


def draw_images(images: List[Union[Image, str]], labels: List[str] = None, display: bool = True) -> Figure:
    """Draw the given list of images onto a single axis.

    Args:
        images: List of images or text to display.
        labels (optional): List of labels for each image. If given, it must be the same length as images.
        display: Whether to display results immediate.

    Returns:
        None if display is set to True, else returns the generated Matplotlib Figure.

    Sample::

        from PIL import Image
        from dosaku.utils import canny, draw_images

        image = Image.open('tests/resources/hopper.png')
        edges = canny(image, mode='RGB')
        draw_images((image, edges), labels=('Original', 'Canny'))

    .. image:: sample_resources/utils_canny.png
    """
    num_images = len(images)
    fig, ax = plt.subplots(1, num_images)
    for i in range(num_images):
        ax[i].set_xticks([])
        ax[i].set_yticks([])
        ax[i].set_xticklabels([])
        ax[i].set_yticklabels([])
        ax[i].spines['left'].set_visible(False)
        ax[i].spines['top'].set_visible(False)
        ax[i].spines['right'].set_visible(False)
        ax[i].spines['bottom'].set_visible(False)
        if isinstance(images[i], Image):
            ax[i].imshow(images[i])
            if images[i].mode == 'L':
                plt.gray()
        elif isinstance(images[i], str):
            ax[i].text(.2, .5, images[i].replace(', ', '\n'), wrap=True)
        if labels is not None:
            ax[i].set_xlabel(labels[i])

    if display:
        plt.show()
    else:
        return fig
