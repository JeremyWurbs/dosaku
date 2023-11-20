"""Utility methods relating to image processing."""
import PIL
from PIL.Image import Image
from typing import Optional

import cv2
import numpy as np

from dosaku.utils import pil_to_cv2, cv2_to_pil, ifnone


def canny(image: Image, low_thresh: int = 100, high_thresh: int = 200, mode='L') -> Image:
    """Computes Canny edges using OpenCV.

    The Canny Edge detector is an algorithm for computing edges in an image. It first computes the gradient across an
    image and then uses two thresholds to determine whether each resulting gradient pixel is part of an edge or not.
    After computing the gradient, the edges are computed from the two threshold values following:

        - If a pixel gradient is higher than the upper threshold, the pixel is considered an edge;
        - If a pixel gradient is lower than the lower threshold, the pixel is considered not an edge;
        - Between the thresholds, it is considered an edge iff it's connected to a pixel that's above the upper thresh.

    The final output is a binary pixel map, where edges are denoted with 1 and non-edges denoted with 0.

    Args:
        image: Input image.
        low_thresh: Lower threshold.
        high_thresh: Upper threshold.
        mode: `Mode of returned image. <https://pillow.readthedocs.io/en/latest/handbook/concepts.html#concept-modes>`_.

    Returns:
        A binary image denoting the computed canny edges. The output image will be the same size as the input image.

    Example::

        from PIL import Image
        from dosaku.utils import canny, draw_images

        image = Image.open('tests/resources/hopper.png')
        edges = canny(image, mode='RGB')
        draw_images((image, edges), labels=('Original', 'Canny'))

    .. image:: sample_resources/utils_canny.png
    """
    edges = cv2.Canny(np.array(image), low_thresh, high_thresh)
    return PIL.Image.fromarray(edges).convert(mode)


def fit(image: Image, height: Optional[int] = None, width: Optional[int] = None) -> Image:
    """Resize image to fit onto canvas while maintaining aspect ratio.

    If the output image has a different aspect ratio than the input image, the output image will center the image with
    transparent borders as necessary.

    Requires that at least one of height or width is given, else the original image is returned unchanged. If only one
    of height and width are given, the other will be computed to keep the aspect ratio the same.

    Args:
        image: Input image.
        height (optional): Height of the output image.
        width (optional): Width of the output image.

    Returns:
        An RGBA image of size height by width, where the original image has been maximally resized to fit in the canvas
        without clipping or cropping. If the aspect ratios between the original and output images are not the same, the
        output image will contain transparent borders as necessary, with the image centered within.

    Example::

        from PIL import Image
        from dosaku.utils import fit, draw_images

        orig_image = Image.open('tests/resources/hopper.png')  # 1024x768 Image
        image = fit(orig_image, width=1440, height=1440)  # 1440x1440 Image
        draw_images((orig_image, image), labels=('Original', 'Fit'))

    .. image:: sample_resources/utils_fit.png
    """
    orig_width, orig_height = image.size
    if height is None and width is None:
        return image
    else:
        if height is None:
            height = int((width / orig_width) * orig_height)
        elif width is None:
            width = int((height / orig_height) * orig_width)

    ratio_width = width / orig_width
    ratio_height = height / orig_height
    ratio = min(ratio_width, ratio_height)

    image = image.resize((int(ratio * image.size[0]), int(ratio * image.size[1])))

    if ratio_width < ratio_height:  # Need to add padding to the top and bottom
        left = 0
        top = int((height - image.size[1]) // 2)
    else:  # Need to add padding to the left and right
        left = int((width - image.size[0]) // 2)
        top = 0
    new_image = PIL.Image.new('RGBA', (width, height))
    new_image.paste(image, (left, top))

    return new_image


def center(image: Image, height: Optional[int] = None, width: Optional[int] = None) -> Image:
    """Center the given image into a height by width canvas with transparent borders.

    If the original image is larger than the output image, it will be resized to fit the canvas. Aspect ratio will be
    preserved.

    Requires that at least one of height or width is given, else the original image is returned unchanged. If only one
    of height and width are given, the other will be kept the same as the original image.

    Args:
        image: Input image.
        height (optional): Height of the output image.
        width (optional): Width of the output image.

    Returns:
        An RGBA image of size height by width, where the original image has been copied and centered without resizing.
        Transparent borders will be added as padding as necessary.

    Example::

        from PIL import Image
        from dosaku.utils import center, draw_images

        orig_image = Image.open('tests/resources/hopper.png')  # 1024x768 Image
        image = center(orig_image, width=1440, height=1080)  # 1080x1440 Image
        draw_images((orig_image, image), labels=('Original', 'Center'))

    .. image:: sample_resources/utils_center.png
    """
    orig_width, orig_height = image.size
    if height is None and width is None:
        return image
    else:
        if height is None:
            return fit(image, height=orig_height, width=width)
        elif width is None:
            return fit(image, height=height, width=orig_width)

    left = int((width - image.size[0]) // 2)
    top = int((height - image.size[1]) // 2)
    new_image = PIL.Image.new('RGBA', (width, height))
    new_image.paste(image, (left, top))

    return new_image


def erode(image: Image, mode='L', iterations=1):
    """Compute the morphological erosion for an image.

    Args:
        image: Input image.
        mode: `Mode of returned image. <https://pillow.readthedocs.io/en/latest/handbook/concepts.html#concept-modes>`_.
        iterations: Number of times to apply the erosion.

    Returns:
        A binary image denoting the computed eroded edges. The output image will be the same size as the input image.
    """
    kernel = np.asarray(cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    erode_image = cv2.erode(pil_to_cv2(image), kernel, iterations=iterations)
    return cv2_to_pil(erode_image).convert(mode)


def binary_mask_to_alpha(mask: Image, blur_radius: int = None) -> Image:
    """Convert a binary mask to an alpha mask with optional Gaussian blurring.

    Refer to `this post <https://stackoverflow.com/a/47724333>`_ for information on how PIL handles mask images. In
    short, this function converts a PIL Image in mode '1' or 'L' to one in mode 'RGBA'.

    If a blur_radius is provided, the binary mask will be blurred around the edges, yielding a "soft mask".

    Args:
        mask: Input image, should be a PIL Image in mode '1' or 'L'.
        blur_radius (optional): The blur radius (ksize) passed into cv2.GaussianBlur.

    Returns:
        A binary PIL mask image in mode 'RGBA', where the alpha channel contains the mask.
    """
    if blur_radius is None:
        return mask.convert('RGBA')

    else:
        cv2_mask = pil_to_cv2(mask)
        grayscale_mask = cv2.cvtColor(cv2_mask, cv2.COLOR_BGR2GRAY)
        blurred_mask = cv2.GaussianBlur(grayscale_mask, (blur_radius, blur_radius), 0)
        normalized_mask = cv2.normalize(blurred_mask, None, 0, 255, cv2.NORM_MINMAX)
        alpha_mask = np.zeros(cv2_mask.shape[:2], dtype=np.uint8)
        alpha_mask[:, :] = normalized_mask

        return cv2_to_pil(alpha_mask).convert('RGBA')


def insert_image(
        destination_image: Image,
        source_image: Image,
        source_mask: Image = None,
        source_width: int = None,
        source_height: int = None,
        left: int = 0,
        top: int = 0):
    """Resize and insert an image into another at a given location.

    If at least one of source_width or source_height are given, the source image will be resized to (source_width,
    source_height). If only one of these values is given, the other will be computed to maintain the source image aspect
    ratio.

    Args:
        destination_image: The image onto which the source image is inserted.
        source_image: The image to insert onto the destination image.
        source_mask (optional): If given, the source image will be masked according to the source mask. The source mask
            must be the same resolution as the source image and have one of the following modes: '1', 'L', 'LA' or
            'RGBA'. In the case mode is 'LA' or 'RGBA', the alpha channel will be used as the mask.
        source_width (optional): If given, the width to resize source image.
        source_height (optional):  If given, the height to resize the source image.
        left: The destination x-coordinate to paste the (top left corner of the) source image.
        top: The destination y-coordinate to paste the (top left corner of the) source image.

    Returns:
        An image. The returned image will have mode 'RGB' and the same resolution as the destination image.

    Example::

        from PIL import Image
        from dosaku.utils import insert_image, draw_images

        destination_image = Image.open('tests/resources/background.png')
        source_image = Image.open('tests/resources/hopper.png')
        source_mask = Image.open('tests/resources/hopper_mask.png')
        image = insert_image(
                    destination_image,
                    source_image,
                    source_mask,
                    source_width=500,
                    left=250,
                    top=100)
        draw_images((destination_image, source_image, source_mask, image),
                    labels=('destination_image', 'source_image', 'source_mask', 'output image'))

    .. image:: sample_resources/utils_insert_image.png
    """
    # First check if we will be editing the source image. If so, create a new copy so that we do not edit the original.
    if any((val is not None for val in [source_mask, source_width, source_height])):
        source_image = source_image.copy()

    if source_mask is not None:
        if source_mask.mode in ['LA', 'RGBA']:
            new_mask = PIL.Image.new(mode='L', size=source_mask.size)
            new_mask.paste(source_mask.split()[-1])
            source_mask = new_mask
        if source_mask.mode not in ['L', '1']:
            raise AssertionError(f'The source_mask mode must be one of ["1", "L", "LA", "RGBA"], '
                                 f'found "{source_mask.mode}".')
        if source_image.size != source_mask.size:
            raise AssertionError(f'The source_image and source_mask must be the same size, '
                                 f'found {source_image.size} and {source_mask.size}, respectively.')

        source_image.putalpha(source_mask)

    if source_width is not None or source_height is not None:
        if source_width is None:
            source_width = int(source_image.size[0] * source_height / source_image.size[1])
        if source_height is None:
            source_height = int(source_image.size[1] * source_width / source_image.size[0])
        source_image = source_image.resize((source_width, source_height))

    output_image = destination_image.copy().convert(mode='RGB')
    if source_mask is not None:
        output_image.paste(source_image, (left, top), mask=source_image)
    else:
        output_image.paste(source_image, (left, top))

    return output_image
