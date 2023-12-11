from PIL.Image import Image
from typing import List, Optional, Protocol

from dosaku.types import Audio, Message


class BackendAgent(Protocol):
    def __init__(self):
        super().__init__()

    def commands(self) -> List[str]:
        raise NotImplementedError

    def chat(self, text: str) -> Message:
        raise NotImplementedError

    def text_to_speech(self, text: str) -> Audio:
        raise NotImplementedError

    def text_to_image(self, prompt: str) -> Image:
        raise NotImplementedError

    def transcribe_audio(self, audio: Audio) -> str:
        raise NotImplementedError

    def transcribe_interview_audio(
            self,
            audio: Audio,
            interviewer: Optional[str] = None,
            interviewee: Optional[str] = None
    ) -> str:
        return self.transcribe_audio(audio)

    def voices(self) -> List[str]:
        raise NotImplementedError

    def voice(self, voice: str) -> None:
        raise NotImplementedError
