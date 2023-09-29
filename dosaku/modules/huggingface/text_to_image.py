from typing import Optional

from diffusers import DiffusionPipeline

from dosaku import Config, Module
#from dosaku.tasks import TextToImageTask


class TextToImage(Module):
    config = Config()
    name = 'TextToImage'

    def __init__(self, device='cuda', enable_cpu_offloading=True, enable_xformers_memory_efficient_attention=False):
        super().__init__()
        self.model = DiffusionPipeline.from_pretrained(
            self.config['DIFFUSERS_DIFFUSION_PIPELINE']['TEXT_TO_IMAGE']).to(device)
        if enable_cpu_offloading:
            self.model.enable_sequential_cpu_offload()
        if enable_xformers_memory_efficient_attention:
            self.model.enable_xformers_memory_efficient_attention()

    def text_to_image(self, prompt: str, negative_prompt: Optional[str], **kwargs):
        return self.model(prompt=prompt, negative_prompt=negative_prompt, **kwargs)
