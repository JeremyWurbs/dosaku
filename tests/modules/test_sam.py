"""Unit test methods for dosaku.modules.meta.segment_anything.SegmentAnything class."""
from PIL.Image import Image

from supervision import MaskAnnotator

from dosaku.modules import SegmentAnything, Yolo8
from dosaku.utils import pil_to_cv2, cv2_to_pil
from tests import MockAssets


def compute_mask(sam: SegmentAnything, image: Image):
    yolo = Yolo8()
    detections = yolo(image)
    detections = detections[detections.class_id == 0]  # Filter out only person detections
    mask = sam.compute_mask(bbox=detections[0].xyxy.astype('int'), image=image)

    assert isinstance(mask, Image)


def detect(sam: SegmentAnything, image):
    detections = sam.detect(image)

    mask_image = MaskAnnotator().annotate(pil_to_cv2(image), detections=detections)
    pil_mask = cv2_to_pil(mask_image)

    assert isinstance(pil_mask, Image)
    assert len(detections) > 0  # SAM is unable to classify detections, but it should have detected at least something


def test_all_sams(image: Image = MockAssets.image):
    image = image.resize((image.size[0] // 8, image.size[0] // 8))  # Resize image to avoid out-of-memory errors

    for sam_type in ['vit_b', 'vit_l', 'vit_h']:
        sam = SegmentAnything(sam_type=sam_type)
        compute_mask(sam, image=image)
        detect(sam, image=image)
