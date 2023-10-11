"""Wrapper class around the official Stable Diffusion pipelines from diffusers."""
from enum import Enum
from typing import Optional, Union

from diffusers import DiffusionPipeline

from dosaku import Module


class StableDiffusion(Module):
    """Stable Diffusion wrapper class.

    The officially supported versions are listed in StableDiffusion.Models. To wrap other models that may be
    released in the future, you may pass the hugging face name (model_name_or_path variable) in directly.

    Args:
        model_version: The model architecture to load. Expects one of the models listed in StableDiffusion.Models.
        model_name: If given, it will override the model_version.
        device: The cpu/cuda device to move the model to.
        variant: Generally one of {'fp16', 'fp32'}, although some models may support other (e.g. 'bf16') formats.
        use_safetensors: Whether to use the safetensor format.
        enable_cpu_offloading: Whether to enable cpu offloading. Set to True if you are having gpu memory issues.
        enable_xformers_memory_efficient_attention: Whether to use xformers.

    Example::

        from dosaku import Agent

        agent = Agent()
        agent.learn('StableDiffusion', model_version='1.5')
        image = agent.StableDiffusion('an astronaut riding a horse').images[0]
        image.show()

    .. image:: sample_resources/stable_diffusion.png
    """
    name = 'StableDiffusion'

    class Models(str, Enum):
        """List of supported Stable Diffusion versions."""
        SD1P1 = '1.1'
        SD1P2 = '1.2'
        SD1P3 = '1.3'
        SD1P4 = '1.4'
        SD1P5 = '1.5'
        SD2 = '2'
        SD2P1 = '2.1'
        SD2P1BASE = '2.1BASE'
        XLBASE = 'XLBASE'
        XLREFINER = 'XLREFINER'

    def __init__(
            self,
            model_version: Optional[Union[str, Models]] = '1.5',
            model_name: Optional[str] = None,
            device: str = 'cuda',
            variant: str = 'fp16',
            use_safetensors: bool = True,
            enable_cpu_offloading: bool = False,
            enable_xformers_memory_efficient_attention: bool = True,
            **kwargs):
        super().__init__()

        if model_name is not None:
            self.model_name = model_name
        else:
            if model_version == '1.1':
                self.model_name = 'CompVis/stable-diffusion-v1-1'
            elif model_version == '1.2':
                self.model_name = 'CompVis/stable-diffusion-v1-2'
            elif model_version == '1.3':
                self.model_name = 'CompVis/stable-diffusion-v1-3'
            elif model_version == '1.4':
                self.model_name = 'CompVis/stable-diffusion-v1-4'
            elif model_version == '1.5':
                self.model_name = 'runwayml/stable-diffusion-v1-5'
            elif model_version == '2':
                self.model_name = 'stabilityai/stable-diffusion-2'
            elif model_version == '2.1':  # 768x768 Version
                self.model_name = 'stabilityai/stable-diffusion-2-1'
            elif model_version == '2.1BASE':  # 512x512 Version
                self.model_name = 'stabilityai/stable-diffusion-2-1-base'
            elif model_version == 'XLBASE':
                self.model_name = 'stabilityai/stable-diffusion-xl-base-1.0'
            elif model_version == 'XLREFINER':
                self.model_name = 'stabilityai/stable-diffusion-xl-refiner-1.0'
            else:
                raise NotImplementedError(f'Unknown model_version {model_version}. Pass in the model_name for this '
                                          f'model to use.')

        self.model = DiffusionPipeline.from_pretrained(
            self.model_name,
            variant=variant,
            use_safetensors=use_safetensors,
            **kwargs
        ).to(device)

        if enable_cpu_offloading:
            self.model.enable_sequential_cpu_offload()

        if enable_xformers_memory_efficient_attention:
            self.model.enable_xformers_memory_efficient_attention()

    def __call__(self, *args, **kwargs):
        return self.model(*args, **kwargs)

    def to(self, *args, **kwargs):
        self.model.to(*args, **kwargs)

    @property
    def device(self):
        return self.model.device


StableDiffusion.register_action('__call__')
StableDiffusion.register_task('StableDiffusion')
StableDiffusion.register_task('TextToImage')
