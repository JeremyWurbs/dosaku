"""Unit test methods for dosaku.modules.stability.sd_official.StableDiffusion class."""
from PIL.Image import Image
import pytest

from dosaku import Module
from dosaku.modules import StableDiffusion
from tests import MockAssets

mocks = MockAssets()


def test_stable_diffusion(image: Image = mocks.image_square):

    # Test all known models from StableDiffusion.Models
    for model_type in StableDiffusion.Models:
        print(f'Testing {model_type}..')
        model = StableDiffusion(model_version=model_type, device='cuda', enable_cpu_offloading=True)
        if model_type == StableDiffusion.Models.XLREFINER:
            output_image = model(prompt=MockAssets.prompt, image=image, num_inference_steps=5).images[0]
        else:
            output_image = model(prompt=MockAssets.prompt, num_inference_steps=5).images[0]
        assert isinstance(output_image, Image)
        assert isinstance(model, Module)

    # Test passing in model_name directly
    print(f'Testing {"runwayml/stable-diffusion-v1-5"}..')
    model = StableDiffusion(model_name='runwayml/stable-diffusion-v1-5', device='cuda', enable_cpu_offloading=False)
    output_image = model(prompt=MockAssets.prompt, num_inference_steps=5).images[0]
    assert isinstance(output_image, Image)
    assert isinstance(model, Module)

    # Test manually moving the model to and from the gpu
    model.to('cuda')
    assert model.device.type == 'cuda'
    model.to('cpu')
    assert model.device.type == 'cpu'

    # Test that an exception is thrown if there is no model_name given and model_version is unknown:
    with pytest.raises(Exception):
        model = StableDiffusion(model_version='SD3000')
        output_image = model(prompt=MockAssets.prompt, num_inference_steps=5).images[0]
        assert isinstance(output_image, Image)
