from PIL import Image
import requests

from dosaku import Config
from dosaku.utils import pil_to_bytes, bytes_to_pil, center


class Clipdrop:
    """Clipdrop wrapper class around Stability AI's Clipdrop API.

    Clipdrop requires an API key to use. Put the API key in dosaku/config/config.ini.
    """
    config = Config()

    def text_to_image(self, prompt: str) -> Image:
        """Replaces the background according to the prompt.

        Args:
            prompt: Input prompt.

        Returns:
            An image generated according to the prompt.

        Example::

            from dosaku.apis import Clipdrop

            cd = Clipdrop()
            prompt = 'An astronaut riding on a horse.'
            image = cd.text_to_image(prompt)
            image.show()

        .. image:: sample_resources/clipdrop_text_to_image.png
        """
        response = requests.post(self.config['CLIPDROP']['TEXT_TO_IMAGE_URL'],
                                 files={'prompt': (None, prompt, 'text/plain')},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()

    def remove_background(self, image: Image, crop=False) -> Image:
        """Removes background from the image.

        Args:
            image: Input image.
            crop: Whether to crop the resulting foreground image.

        Returns:
            An RGBA Image with the background removed (alpha channel set to transparent). If crop is set to true the
            image will be cropped to the smallest encompassing bbox image.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            image = Image.open('tests/resources/hopper.png')
            foreground = cd.remove_background(image, crop=True)
            draw_images((image, foreground), labels=('Original', 'Foreground'))

        .. image:: sample_resources/clipdrop_remove_background.png
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['REMOVE_BACKGROUND_URL'],
                                 files={'image_file': ('original.png', image_bytes, 'image/png')},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            foreground_image = bytes_to_pil(response.content)

            if crop:
                bbox = foreground_image.getbbox()
                image_crop = foreground_image.crop(bbox)
                foreground_image = center(image_crop)

            return foreground_image

        else:
            response.raise_for_status()

    def replace_background(self, prompt: str, image: Image) -> Image:
        """Replaces the background according to the prompt.

        Args:
            image: Input image.
            prompt: Prompt describing the background.

        Returns:
            An image with the background removed and inpainted according to the prompt.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            prompt = 'Bustling city street on a rainy day.'
            image = Image.open('tests/resources/hopper.png')
            image_with_background = cd.replace_background(prompt, image)
            draw_images((image, image_with_background), labels=(f'Original', 'Added Background'))

        .. image:: sample_resources/clipdrop_replace_background.png
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['REPLACE_BACKGROUND_URL'],
                                 files={'image_file': ('original.png', image_bytes, 'image/png')},
                                 data={'prompt': prompt},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()

    def remove_text(self, image: Image, extension: str = 'png') -> Image:
        """Removes text from the image.

        Args:
            image: Input image.

        Returns:
            An image with the text removed and image inpainted.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            image = Image.open(''tests/resources/keep_calm.jpg')
            image_notext = cd.remove_text(image, extension='jpg')
            draw_images((image, image_notext), labels=('Original', 'No Text'))

        .. image:: sample_resources/clipdrop_remove_text.png
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['REMOVE_TEXT_URL'],
                                 files={'image_file': (f'original.{extension}', image_bytes, f'image/{extension}')},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()

    def upscale(self, image: Image, width: int, height: int) -> Image:
        """Upscales the image to the given resolution.

        Args:
            image: Input image.
            width: Output image width. Must be between 1 and 4096.
            height: Output image height. Must be between 1 and 4096.

        Returns:
            An Image with the given resolution.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            image = Image.open('tests/resources/hopper.png')
            upscale = cd.upscale(image, height=1920, width=1280)
            draw_images((image, upscale), labels=('Original', 'Upscaled'))

        .. image:: sample_resources/clipdrop_upscale.png

        .. image:: sample_resources/clipdrop_upscale_closeup.png
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['UPSCALE_URL'],
                                 files={'image_file': ('original.png', image_bytes, 'image/png')},
                                 data={'target_width': width, 'target_height': height},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)

        else:
            response.raise_for_status()

    def inpaint(self, image: Image, mask: Image) -> Image:
        """Inpaint the masked region into the image.

        Note that the inpaint model appears to have been trained to make objects disappear. It does not work well for
        trying to add objects into a scene, such as adding new items of clothing onto a person.

        Args:
            image: Input image.
            mask: Binary mask image. The masked region (area denoted by 1s) will be removed and inpainted.

        Returns:
            An Image with the given resolution.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            image = Image.open('tests/resources/hopper.png')
            mask = Image.open('tests/resources/hopper_mask.png')
            inpaint = cd.inpaint(image, mask)
            draw_images((image, mask, inpaint), labels=('Original', 'Mask', 'Inpaint'))

        .. image:: sample_resources/clipdrop_inpaint.png
        """
        image_bytes = pil_to_bytes(image)
        mask_bytes = pil_to_bytes(mask)

        response = requests.post(self.config['CLIPDROP']['INPAINT_URL'],
                                 files={'image_file': ('original.png', image_bytes, 'image/png'),
                                        'mask_file': ('mask.png', mask_bytes, 'image/png')},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()

    def portrait_depth(self, image: Image) -> Image:
        """Estimates depth map for a portrait image.

        Args:
            image: Input image.

        Returns:
            A portait depth map image.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            image = Image.open('tests/resources/hopper.png')
            depth_map = cd.portrait_depth(image)
            draw_images((image, depth_map), labels=('Original', 'Depth Map'))

        .. image:: sample_resources/clipdrop_portrait_depth.png
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['PORTRAIT_DEPTH_URL'],
                                 files={'image_file': ('original.png', image_bytes, 'image/png')},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()

    def portrait_surface_normals(self, image: Image) -> Image:
        """Estimates surface normals for a portrait image.

        Args:
            image: Input image.

        Returns:
            A surface normal image.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            image = Image.open('tests/resources/hopper.png')
            depth_map = cd.portrait_surface_normals(image)
            draw_images((image, depth_map), labels=('Original', 'Surface Normals'))

        .. image:: sample_resources/clipdrop_surface_normals.png
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['PORTRAIT_SURFACE_NORMALS_URL'],
                                 files={'image_file': ('original.png', image_bytes, 'image/png')},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()

    def sketch_to_image(self, prompt: str, image: Image, extension: str = 'png') -> Image:
        """Generates an image according to the supplied sketch and prompt.

        The sketch should be black sketch lines on a white background in a PNG, JPEG or WebP file, with a maximum width
        and height of 1024 pixels. Fow now, only square images are supported.

        Args:
            image: Input image.
            prompt: Prompt describing the image to generate.

        Returns:
            An image matching the sketch and prompt.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            prompt = 'Man standing alone in a post apocalyptic barren wasteland.'
            sketch = Image.open('tests/resources/hopper.png')
            image = cd.sketch_to_image(prompt, sketch, extension='jpg')
            draw_images((sketch, image), labels=(f'Sketch', 'Image'))

        .. warning::
            The Sketch-to-Image API has not been tested successfully. It appears to be an issue on the API side.
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['SKETCH_TO_IMAGE_URL'],
                                 files={'image_file': (f'original.{extension}', image_bytes, f'image/{extension}')},
                                 data={'prompt': prompt},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()

    def reimagine(self, image: Image) -> Image:
        """Generates a variation of the input image, "similar but different".

        Args:
            image: Input image.

        Returns:
            An image with similar content to the input image.

        Example::

            from PIL import Image
            from dosaku.apis import Clipdrop
            from dosaku.utils import draw_images

            cd = Clipdrop()
            image = Image.open('tests/resources/hopper.png')
            variation = cd.reimagine(image)
            draw_images((image, variation), labels=('Original', 'Variation'))

        .. image:: sample_resources/clipdrop_reimagine.png
        """
        image_bytes = pil_to_bytes(image)

        response = requests.post(self.config['CLIPDROP']['REIMAGINE_URL'],
                                 files={'image_file': ('original.png', image_bytes, 'image/png')},
                                 headers={'x-api-key': self.config['API_KEYS']['CLIPDROP']})

        if response.ok:
            return bytes_to_pil(response.content)
        else:
            response.raise_for_status()
