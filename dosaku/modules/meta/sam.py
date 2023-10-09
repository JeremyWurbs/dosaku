"""Meta's SegmentAnything module."""
import os
from PIL.Image import Image
from typing import Optional

import numpy as np
from segment_anything import SamPredictor, sam_model_registry, SamAutomaticMaskGenerator
import supervision as sv

from dosaku import Config, Module
from dosaku.utils import pil_to_ndarray, ndarray_to_pil


class SegmentAnything(Module):
    """Meta's SegmentAnything.

    Args:
        model_path: Path to the model pth file. If not given the location in the user's config file will be used.
        sam_type: The model type to use. One of {'vit_h', 'vit_l', 'vit_b'}. Refer to the official
        `github <https://github.com/facebookresearch/segment-anything#model-checkpoints>`_ page for more information.
    """
    name = 'SegmentAnything'
    config = Config()

    def __init__(self, model_path: Optional[str] = None, sam_type: str = 'vit_h', device='cuda'):
        super().__init__()

        if model_path is None:
            if sam_type == 'vit_h':
                model_path = os.path.join(self.config['MODELS']['SAM_DIR'], 'sam_vit_h_4b8939.pth')
            elif sam_type == 'vit_l':
                model_path = os.path.join(self.config['MODELS']['SAM_DIR'], 'sam_vit_l_0b3195.pth')
            elif sam_type == 'vit_b':
                model_path = os.path.join(self.config['MODELS']['SAM_DIR'], 'sam_vit_b_01ec64.pth')

        weights = sam_model_registry[sam_type](checkpoint=model_path).to(device)
        self.model = SamPredictor(weights)
        self.mask_generator = SamAutomaticMaskGenerator(weights)

    def set_image(self, image: Image):
        """Calculate the SAM embeddings for the given image.

        Note that nothing is returned from this method. Instead, subsequent predictions will use the computed
        embeddings. This setup allows for multiple predictions / mask generations without having to recompute the image
        embeddings.
        """
        image = pil_to_ndarray(image, 'RGB')
        self.model.set_image(image)

    def compute_mask(self, bbox: np.ndarray, image: Optional[Image] = None) -> Image:
        """Generate mask for the object at the given bounding box location.

        Example::

            from PIL import Image
            from dosaku import Agent
            from dosaku.utils import draw_images

            image = Image.open('tests/resources/hopper.png')

            agent = Agent()
            agent.learn('ObjectDetection')
            agent.learn('SegmentAnything')

            detections = agent.ObjectDetection(image)
            detections = detections[detections.class_id == 0]  # Get bounding boxes just for "person"
            mask = agent.SegmentAnything.compute_mask(bbox=detections.xyxy.astype('int'), image=image)

            draw_images((image, mask), labels=('Original Image', 'Generated Mask'))

        .. image:: sample_resources/pipelines_sam_mask.png
        """
        if image is not None:
            self.set_image(image)
        mask, _, _ = self.model.predict(
            box=bbox[None, :],
            point_coords=None,
            point_labels=None,
            multimask_output=False)

        return ndarray_to_pil(np.squeeze(mask))

    def detect(self, image: Image) -> sv.Detections:
        """Detect objects in an image.

        Note that SegmentAnything, by itself, will not provide any labels for the detected objects.

        Example::

            from PIL import Image
            from supervision import MaskAnnotator
            from dosaku import SegmentAnything as SAM
            from dosaku.utils import pil_to_cv2, cv2_to_pil

            image = Image.open('tests/resources/hopper.png')
            sam = SAM()
            detections = sam.detect(image)
            for (x1, y1, x2, y2), mask, confidence, class_id, tracker_id in detections:
                print(f'x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}')
                print(f'mask: {mask.shape} {type(mask)} of type {mask.dtype}')
                print(f'confidence: {confidence}')
                print(f'class_id: {class_id}')
                print(f'tracker_id: {tracker_id}')

            print(f'Total number of detections: {len(detections)}')

            annotator = MaskAnnotator()
            mask_image = annotator.annotate(pil_to_cv2(image), detections=detections)
            cv2_to_pil(mask_image).show()

        .. image:: sample_resources/pipelines_sam_detections.png
        """
        image = pil_to_ndarray(image, 'RGB')
        masks = self.mask_generator.generate(image)
        return sv.Detections.from_sam(masks)


SegmentAnything.register_action('set_image')
SegmentAnything.register_action('compute_mask')
SegmentAnything.register_action('detect')
SegmentAnything.register_task('SegmentAnything')
