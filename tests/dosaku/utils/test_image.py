"""Unit test methods for dosaku.utils.image utility module."""
from PIL.Image import Image
import pytest

from dosaku.utils import canny, fit, center, erode, binary_mask_to_alpha, insert_image
from tests import MockAssets, images_are_identical


mocks = MockAssets()


def test_canny(image: Image = mocks.image):
    edges = canny(image, mode='RGB')
    assert isinstance(edges, Image)


def test_fit(
        image: Image = mocks.image_square,
        wide_image: Image = mocks.image_wide,
        tall_image: Image = mocks.image_tall):

    # Test normal usage
    output_image = fit(image, width=1440, height=1440)
    assert isinstance(output_image, Image)

    # Test when only one of height / width are given
    output_image = fit(image, width=1440, height=None)
    assert isinstance(output_image, Image)
    output_image = fit(image, width=None, height=1440)
    assert isinstance(output_image, Image)

    # Test when neither height nor width are given
    output_image = fit(image, width=None, height=None)
    assert images_are_identical(image, output_image)

    # Test non-square images
    output_image = fit(wide_image, width=1440, height=1440)
    assert isinstance(output_image, Image)
    output_image = fit(tall_image, width=1440, height=1440)
    assert isinstance(output_image, Image)


def test_center(
        image: Image = mocks.image_square,
        wide_image: Image = mocks.image_wide,
        tall_image: Image = mocks.image_tall):

    # Test normal usage
    output_image = center(image, width=1440, height=1080)  # 1440x1080 Image
    assert isinstance(output_image, Image)

    # Test when only one of height / width are given
    output_image = center(image, width=1440, height=None)
    assert isinstance(output_image, Image)
    output_image = center(image, width=None, height=1440)
    assert isinstance(output_image, Image)

    # Test when neither height nor width are given
    output_image = center(image, width=None, height=None)
    assert images_are_identical(image, output_image)

    # Test non-square images
    output_image = center(wide_image, width=1440, height=1440)
    assert isinstance(output_image, Image)
    output_image = center(tall_image, width=1440, height=1440)
    assert isinstance(output_image, Image)


def test_erode(image: Image = mocks.image):
    output_image = erode(image)
    assert isinstance(output_image, Image)


def test_binary_mask_to_alpha(image: Image = mocks.image_mask):
    output_image = binary_mask_to_alpha(image, blur_radius=None)
    assert isinstance(output_image, Image)
    assert output_image.mode == 'RGBA'

    output_image = binary_mask_to_alpha(image, blur_radius=5)
    assert isinstance(output_image, Image)
    assert output_image.mode == 'RGBA'


def test_insert_image(
        destination_image: Image = mocks.image_background,
        source_image: Image = mocks.image,
        source_mask: Image = mocks.image_mask,
        source_mask_with_alpha_channel: Image = mocks.image_rgba):

    # Test normal usage
    output_image = insert_image(destination_image, source_image, source_mask, source_width=500, left=250, top=100)
    assert isinstance(output_image, Image)

    # Test RGBA mask
    output_image = insert_image(destination_image, source_image, source_mask.convert(mode='RGBA'))
    assert isinstance(output_image, Image)

    # Test that a non-binary mask with no alpha channel raises an exception
    with pytest.raises(Exception):
        output_image = insert_image(destination_image, source_image, source_mask.convert(mode='RGB'))
        assert isinstance(output_image, Image)

    # Test that an exception is raised if the source and mask images are not the same size
    with pytest.raises(Exception):
        output_image = insert_image(destination_image, source_image, source_mask.resize((100, 100)))
        assert isinstance(output_image, Image)

    # Test passing in the mask directly through the 'LA'/'RGBA' source image instead of a mask
    output_image = insert_image(destination_image, source_mask_with_alpha_channel)
    assert isinstance(output_image, Image)
