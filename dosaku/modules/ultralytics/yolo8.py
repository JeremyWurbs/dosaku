"""Ultralytics Yolo8 module."""
from PIL.Image import Image

from ultralytics import YOLO
import supervision as sv

from dosaku import Module


class Yolo8(Module):
    """Yolo8 object detection.

    Yolo8 is an object detection model, state of the art as of 2023. Refer to the associated
    `github <https://github.com/ultralytics/ultralytics>`_ for more information.

    Args:
        model_size: The model architecture to load. Expects one of {'n', 's', 'm', 'l', 'x'}.

    Example::

        from PIL import Image
        from supervision import BoxAnnotator
        from dosaku import Yolo8
        from dosaku.utils import pil_to_cv2, cv2_to_pil

        image = Image.open('resources/sunglasses_bunny.png')
        model = Yolo8()
        detections = model(image)

        box_image = BoxAnnotator().annotate(pil_to_cv2(image), detections=detections)
        cv2_to_pil(box_image).show()

    .. image:: sample_resources/pipelines_yolo8.png
    """
    name = 'Yolo8'

    def __init__(self, model_size: str = 'x', device='cuda'):
        super().__init__()
        self.model = YOLO('yolov8' + model_size + '.pt').to(device)

    def detect(self, image: Image, **_) -> sv.Detections:
        detections = self.model.predict(image, verbose=False)[0]
        return sv.Detections.from_ultralytics(detections)

    def __call__(self, image: Image) -> sv.Detections:
        return self.detect(image)


Yolo8.register_task('ObjectDetection')
Yolo8.register_task('SVObjectDetection')
