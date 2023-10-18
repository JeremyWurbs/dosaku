# Built-in Modules

Dosaku comes with a number of capabilities provided by built-in modules. Here we give examples for some of the more 
prominent capabilities. 

Note that we use the term *Module* to denote code / models that are downloaded and run on your local machine, and 
*Service* to denote models that run on through a web service. Services, in general, do not require downloading any 
models to your local machine, but do require setting up an account with the associated service, and generally cost money 
to use.

## Text-to-Image

### Module (Local)

The most capable text-to-image model currently available open source is the stable diffusion model, developed and 
[released](https://github.com/Stability-AI/stablediffusion) by Stability AI. There are numerous versions of stable 
diffusion, all of which have been officially released through Huggingface's diffusers library. We wrap these models into 
their own stable diffusion module.

```python
from dosaku import Agent

agent = Agent()
agent.learn('StableDiffusion', model_version='1.5')
image = agent.StableDiffusion('an astronaut riding a horse').images[0]
image.show()
```

The most recent stable diffusion model is Stable Diffusion XL (SDXL). The SDXL model is actually *two* models: a base 
model and a refiner model. In the ideal case, the base model is used to do ~70% of the processing, with the refiner 
model doing the final ~30%. Unfortunately, it can be a difficult to load both models at the same time, as they cannot 
both fit on a single 24gb card (e.g. a 4090) without some extra work. 

Dosaku offers the combined SDXL model through a separate SDXLEnsembleOfExperts module. Trying to put one or both of the 
models on a CPU will technically work, but will take many (~10-15) minutes to generate a single image. Some helpful 
tips:

- If you have multiple GPUs, put the two models on different GPUs with the `base_device` and `refiner_device` 
arguments:

        agent.learn('SDXLEnsembleOfExperts', base_device='cuda:0', refiner_device='cuda:1')

- If you are having memory issues, use the fp16 models (instead of the default fp32 models):

        agent.learn('SDXLEnsembleOfExperts', 
                    base_kwargs={'variant': 'fp16', 'use_safetensors': True},
                    refiner_kwargs={'variant': 'fp16', 'use_safetensors': True})

- Another way to help with memory issues is to enable cpu offloading, which will offload parts of the model not being 
used. Doing so will slow down processing, but will enable GPU processing in situations where one or both of the models 
would otherwise not be able to fit on the GPU:

       agent.learn('SDXLEnsembleOfExperts', 
                   base_kwargs={'variant': 'fp16', 'use_safetensors': True},
                   refiner_kwargs={'variant': 'fp16', 'use_safetensors': True},
                   enable_cpu_offloading=True)
                
```python
from dosaku import Agent

agent = Agent()
agent.learn('SDXLEnsembleOfExperts', 
            base_kwargs={'variant': 'fp16', 'use_safetensors': True},
            refiner_kwargs={'variant': 'fp16', 'use_safetensors': True},
            enable_cpu_offloading=True)
image = agent.SDXLEnsembleOfExperts('an astronaut riding a horse').images[0]
image.show()
```

### Service (Interwebs)

Stability AI makes their stable diffusion models available through a API service called Clipdrop. Dosaku wraps Clipdrop
into its own module, making a number of image generation utilities available, including text-to-image, background 
change, inpainting and more. 

To make use of Clipdrop, first go to the [official Clipdrop website](), sign up, and place your API key into your 
Dosaku config file under API_KEYS/CLIPDROP.

```python
from dosaku import Agent

agent = Agent(enable_services=True)
agent.learn('TextToImage', module='ClipdropTextToImage')
image = agent.TextToImage.text_to_image('Dosaku playing a game of go')
image.show()
```

![Dosaku playing go](resources/dosaku.png)
