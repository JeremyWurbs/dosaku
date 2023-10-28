from dosaku.tasks.song_serializer import SongSerializer
from dosaku.tasks.text_to_image import TextToImage
from dosaku.tasks.speech_to_text import SpeechToText
from dosaku.tasks.realtime_speech_to_text import RealtimeSpeechToText
from dosaku.tasks.chat import Chat
from dosaku.tasks.zero_shot_text_classification import ZeroShotTextClassification
from dosaku.tasks.gradio_chat import GradioChat
from dosaku.tasks.gtp_v1 import GoTextProtocolV1
from dosaku.tasks.object_detection.object_detection import ObjectDetection
from dosaku.tasks.object_detection.sv_object_detection import ObjectDetectionSV
from dosaku.tasks.restore_faces import RestoreFaces
from dosaku.tasks.dosaku.write_task import WriteTask
from dosaku.tasks.dosaku.write_module import WriteModule
from dosaku.tasks.dosaku.write_module_from_task import WriteModuleFromTask
from dosaku.tasks.dosaku.text_evaluator import TextEvaluator
from dosaku.tasks.dosaku.logic import (LogicActor,
                                       LogicEvaluator)
