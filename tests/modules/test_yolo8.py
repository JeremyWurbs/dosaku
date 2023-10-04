"""Unit test methods for dosaku.modules.ultralytics.yolo8.Yolo8 class."""
from PIL.Image import Image

from supervision import BoxAnnotator

from dosaku.modules import Yolo8
from dosaku.utils import pil_to_cv2, cv2_to_pil
from tests import MockAssets


def test_inference():

    model = Yolo8()
    detections = model(MockAssets.image)
    detections = detections[detections.class_id == 0]  # Filter out only person detections
    box_image = BoxAnnotator().annotate(pil_to_cv2(MockAssets.image), detections=detections)
    pil_image = cv2_to_pil(box_image)

    assert isinstance(pil_image, Image)
    assert len(detections) == 1  # The test image has identically one person
