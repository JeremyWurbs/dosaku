from PIL.Image import Image
from typing import List, Optional, Tuple
import os

from basicsr.utils import img2tensor, tensor2img
from basicsr.utils.download_util import load_file_from_url as download_model
import cv2
from gfpgan.archs.gfpgan_bilinear_arch import GFPGANBilinear
from gfpgan.archs.gfpganv1_arch import GFPGANv1
from gfpgan.archs.gfpganv1_clean_arch import GFPGANv1Clean
from gfpgan.archs.restoreformer_arch import RestoreFormer
from facexlib.utils.face_restoration_helper import FaceRestoreHelper
import torch
import torch.nn as nn
from torchvision.transforms.functional import normalize

from dosaku import Config, Module
from dosaku.utils import ifnone, pil_to_cv2, cv2_to_pil


class GFPGAN1p4(Module):
    """Face restorer pipeline using GFPGAN v1.4.

    GFPGAN is a GAN model (i.e. **not** a diffusion model) used to restore faces. It can be very useful to use as a
    post-processing step if you have passed or generated images containing faces from a diffusion model, as diffusion
    models often have great difficulty generating non-hideous faces.

    Refer to the `source repo <https://github.com/TencentARC/GFPGAN>`_ for information on customizing this module.
    Here we include a basic module for the following end-to-end process:

        1. Detect and crop out all faces in the image, resizing each face to 512x512;
        2. Use GFPGAN to restore each cropped face;
        3. Use a background upsampler to upsample the rest of the image;
        4. Paste back the restored faces onto the upsampled background image.

    Args:
        model_save_dir: The directory containing the GFPGAN weights. If the file does not exist the weights will be
            downloaded to this location. May alternatively set the model_save_dir in the config.ini file under
            [MODELS][GFPGAN_DIR].
        model_filename: The filename to save / load the weights.
        upscale: The upscaling factor of the final output.
        arch: The GFPGAN architecture. Must be one of {'clean', 'bilinear', 'RestoreFormer', 'original'}.
        channel_multiplier: Channel multiplier for large networks of StyleGAN2.
        background_upsampler: The upsampler for the background (non-face portion of the image).

    Returns:
        A tuple of (cropped_faces, restored_faces, restored_image).

        - **cropped_faces**: A list of 512x512 images, each image containing one cropped face from the input image.
        - **restored_faces**: A list of 512x512 images, each image containing the associated restored face.
        - **restored_image**: An image or None. If a background_upsampler is given, a restored_image will be given back.

    Example::

        from PIL import Image
        from dosaku import GFPGAN1p4
        from dosaku.utils import tensor_to_pil, draw_images

        image = Image.open('tests/resources/disfigured_face.png')

        gfpgan = GFPGAN1p4()
        cropped_faces, restored_faces, restored_image = gfpgan(image)

        draw_images(images=(image, cropped_faces[0], restored_faces[0], restored_image),
                    labels=('Original Image', 'GFPGAN Input', 'GFPGAN Output', 'Restored Image'))

    .. image:: sample_resources/modules_gfpgan1p4.png
    """
    config = Config()

    def __init__(self,
                 model_save_dir: Optional[str] = None,
                 model_filename: str = 'GFPGAN1p4.pth',
                 upscale: float = 2.,
                 arch: str = 'clean',
                 channel_multiplier: int = 2,
                 background_upsampler: Optional[nn.Module] = None):
        super().__init__()

        model_save_dir = ifnone(model_save_dir, self.config['MODELS']['GFPGAN_DIR'])

        weights_dir = os.path.join(model_save_dir, 'weights')
        model_path = os.path.join(weights_dir, model_filename)
        if not os.path.isfile(model_path):
            download_model(
                url='https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth',
                model_dir=weights_dir,
                progress=True,
                file_name=model_filename)
        weights = torch.load(model_path)
        if 'params_ema' in weights:
            keyname = 'params_ema'
        else:
            keyname = 'params'

        if arch == 'original':
            self.model = GFPGANv1(
                out_size=512,
                num_style_feat=512,
                channel_multiplier=channel_multiplier,
                decoder_load_path=None,
                fix_decoder=True,
                num_mlp=8,
                input_is_latent=True,
                different_w=True,
                narrow=1,
                sft_half=True)
        elif arch == 'bilinear':
            self.model = GFPGANBilinear(
                out_size=512,
                num_style_feat=512,
                channel_multiplier=channel_multiplier,
                decoder_load_path=None,
                fix_decoder=False,
                num_mlp=8,
                input_is_latent=True,
                different_w=True,
                narrow=1,
                sft_half=True)
        elif arch == 'clean':
            self.model = GFPGANv1Clean(
                out_size=512,
                num_style_feat=512,
                channel_multiplier=channel_multiplier,
                decoder_load_path=None,
                fix_decoder=False,
                num_mlp=8,
                input_is_latent=True,
                different_w=True,
                narrow=1,
                sft_half=True)
        elif arch == 'RestoreFormer':
            self.model = RestoreFormer()
        else:
            raise AssertionError(f"Unknown architecture {arch}. Must be one of {{'original', 'bilinear', 'clean', 'RestoreFormer'}}.")

        self.face_helper = FaceRestoreHelper(
            upscale,
            face_size=512,
            crop_ratio=(1, 1),
            det_model='retinaface_resnet50',
            save_ext='png',
            use_parse=True,
            device=self.device,
            model_rootpath=weights_dir)

        self.model.load_state_dict(weights[keyname], strict=True)
        self.model.eval()
        self.model = self.model.to(self.device)
        self.background_sampler = background_upsampler

    @torch.no_grad()
    def __call__(
            self,
            image: Image,
            aligned: bool = False,
            only_center_face:
            bool = False,
            paste_back: bool = True,
            weight: float = 0.5
            ) -> Tuple[List[Image], List[Image], Image]:
        """Run the pipeline.

        Args:
            image: The input image.
            aligned: If True, denotes that a single, pre-aligned face is being passed in.
            only_center_face: Whether to only process the center face.
            paste_back: Whether to paste back the faces onto the upsampled image.
        """
        image = pil_to_cv2(image)
        self.face_helper.clean_all()

        if aligned:
            image = cv2.resize(image, (512, 512))
            self.face_helper.cropped_faces = [image]
        else:
            self.face_helper.read_image(image)
            self.face_helper.get_face_landmarks_5(only_center_face=only_center_face, eye_dist_threshold=5)
            self.face_helper.align_warp_face()

        for cropped_face in self.face_helper.cropped_faces:
            cropped_face_t = img2tensor(cropped_face / 255., bgr2rgb=True, float32=True)
            normalize(cropped_face_t, (0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)
            cropped_face_t = cropped_face_t.unsqueeze(0).to(self.device)

            try:
                output = self.model(cropped_face_t, return_rgb=False, weight=weight)[0]
                restored_face = tensor2img(output.squeeze(0), rgb2bgr=True, min_max=(-1, 1))
            except RuntimeError:  # Failed inference for GFPGAN, return original cropped face
                restored_face = cropped_face

            restored_face = restored_face.astype('uint8')
            self.face_helper.add_restored_face(restored_face)

        restored_image = None
        if not aligned and paste_back:
            if self.background_sampler is not None:
                background_image = self.background_sampler.enhance(image, outscale=self.upscale)[0]
            else:
                background_image = None

            self.face_helper.get_inverse_affine(None)
            restored_image = self.face_helper.paste_faces_to_input_image(upsample_img=background_image)
            restored_image = cv2_to_pil(restored_image)

        cropped_faces = [cv2_to_pil(face) for face in self.face_helper.cropped_faces]
        restored_faces = [cv2_to_pil(restored_face) for restored_face in self.face_helper.restored_faces]

        return cropped_faces, restored_faces, restored_image


GFPGAN1p4.register_action('__call__')
GFPGAN1p4.register_task('GFPGAN1p4')
