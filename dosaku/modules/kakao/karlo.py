from diffusers import DiffusionPipeline, ImagePipelineOutput
import torch

from dosaku import Module


class KarloImageBlend(Module):
    """Kakaobrain Karlo Image Interpolator

    Interpolates between two input images using spherical interpolation (slerp) in the embedding space. The number of
    interpolations will be given by the *steps* parameter when called. Due to the interpolation sampling, early outputs
    will be more similar to the first image, with later outputs being more similar to the second image.

    Refer to the associated `Diffusers documentation
    <https://github.com/huggingface/diffusers/blob/main/examples/community/unclip_image_interpolation.py>`_
    for more details.

    Example::

        from PIL import Image
        from dosaku import Agent
        from dosaku.utils import draw_images

        hopper = Image.open('tests/resources/hopper.png')
        image2 = Image.open('tests/resources/image2.png')

        agent = Agent()
        agent.learn('KarloImageBlend')

        blends = agent.KarloImageBlend(image=[snowglobe, owl], steps=7, return_dict=False)[0]
        draw_images([snowglobe] + blends + [owl], labels = ['Input Image 1'] + [f'Output Blend {i+1}' for i in range(7)] + ['Input Image 2'])

    .. image:: sample_resources/pipelines_karlo_blend.png
    """
    name = 'KarloImageBlend'

    def __init__(self, device='cuda', dtype=torch.float16, **kwargs):
        super().__init__()
        self.model = DiffusionPipeline.from_pretrained(
            'kakaobrain/karlo-v1-alpha-image-variations',
            torch_dtype=dtype,
            custom_pipeline='unclip_image_interpolation',
            **kwargs
        ).to(device)

    def __call__(self, *args, **kwargs) -> ImagePipelineOutput:
        return self.model(*args, **kwargs)


KarloImageBlend.register_action('__call__')
KarloImageBlend.register_task('KarloImageBlend')
