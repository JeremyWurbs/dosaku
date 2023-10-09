from diffusers import DiffusionPipeline

from dosaku import Module
from dosaku.utils import ifnone


class SDXLEnsembleOfExperts(Module):
    """Stable Diffusion XL Base + Refiner Model in One Pipeline.

    Example::

        import torch
        from dosaku import Agent
        from dosaku.utils import draw_images

        agent.learn('SDXLEnsembleOfExperts',
            base_kwargs={'variant': 'fp16', 'use_safetensors': True},
            refiner_kwargs={'variant': 'fp16', 'use_safetensors': True},
            base_device='cuda',
            refiner_device='cuda',
            enable_cpu_offloading=True)

        generator = torch.manual_seed(42)
        prompts = [
            'photo of an astronaut riding a horse, 8k, photo realistic',
            'a photograph of an evil and vile looking demon in Bengali attire eating fish. The demon has '
                'large and bloody teeth. The demon is sitting on the branches of a giant Banyan tree, dimly '
                'lit, bluish and dark color palette, realistic, 8k',
            'Hyper detailed portrait of a terrifying werewolf with Fearsome detailed fangs and frightening '
                'detailed eyes, long fur, Cinematic lighting, '
                'composition, Photorealism, Bokeh blur, hyper detailed, '
                'render, shot on Hasselblad H4D 200MS Digital Camera',
            'A highly detained photo of Ganesha with a golden tiara on the head and a snake wrapped around his '
                   'belly. The Himalayan mountains are the backdrop of the photo. Realistic, cold and bright color '
                   'grading, 8k.']
        negative_prompt = ('((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers,
            'mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), '
            'blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), '
            'out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing '
            'arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), '
            '(too many fingers), (((long neck)))')

        images = agent.SDXLEnsembleOfExperts(prompts,
                      negative_prompt=[negative_prompt] * len(prompts),
                      generator=generator).images
        draw_images(images)

    .. image:: sample_resources/pipelines_sdxl_eoe.png
    """
    name = 'SDXLEnsembleOfExperts'

    def __init__(self,
                 base_kwargs: dict = None,
                 refiner_kwargs: dict = None,
                 base_device: str = 'cuda',
                 refiner_device: str ='cuda',
                 enable_cpu_offloading: bool = False):
        super().__init__()

        base_kwargs = ifnone(base_kwargs, default=dict())
        refiner_kwargs = ifnone(refiner_kwargs, default=dict())
        self.base = DiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0', **base_kwargs).to(base_device)
        if enable_cpu_offloading:
            self.base.enable_sequential_cpu_offload()
            self.base.enable_xformers_memory_efficient_attention()
        self.refiner = DiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-xl-refiner-1.0', **refiner_kwargs).to(refiner_device)
        if enable_cpu_offloading:
            self.refiner.enable_sequential_cpu_offload()
            self.refiner.enable_xformers_memory_efficient_attention()

    def __call__(self,
                 prompt=None,
                 prompt_2=None,
                 negative_prompt=None,
                 negative_prompt_2=None,
                 num_inference_steps=100,
                 num_refinement_steps=150,
                 high_noise_fraction=0.8,
                 **kwargs):
        prompt_2 = ifnone(prompt_2, default=prompt)
        negative_prompt = ifnone(negative_prompt, default=[None]*len(prompt) if isinstance(prompt, list) else None)
        negative_prompt_2 = ifnone(negative_prompt_2, default=negative_prompt)

        latents = self.base(prompt=prompt,
                            prompt_2=prompt_2,
                            negative_prompt=negative_prompt,
                            negative_prompt_2=negative_prompt_2,
                            output_type='latent',
                            num_inference_steps=num_inference_steps,
                            denoising_end=high_noise_fraction,
                            **kwargs)

        return self.refiner(prompt=prompt,
                            prompt_2=prompt_2,
                            negative_prompt=negative_prompt,
                            negative_prompt_2=negative_prompt_2,
                            image=latents.images,
                            num_inference_steps=num_refinement_steps,
                            denoising_start=high_noise_fraction,
                            **kwargs)


SDXLEnsembleOfExperts.register_action('__call__')
SDXLEnsembleOfExperts.register_task('SDXLEnsembleOfExperts')
