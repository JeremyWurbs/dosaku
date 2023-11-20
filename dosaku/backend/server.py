from __future__ import annotations
from typing import Optional, TYPE_CHECKING

from fastapi import FastAPI

if TYPE_CHECKING:
    from dosaku import BackendAgent
from dosaku.agents import Dosaku
from dosaku.utils import pil_to_ascii
from dosaku.backend.connection import Connection
from dosaku.backend.types import (ChatInput,
                                  TextToImageInput,
                                  TranscribeInterviewInput,
                                  VoiceInput)


class Server:
    def __init__(self, agent: Optional[BackendAgent] = None):
        self.agent = agent

    def app(self):
        if self.agent is None:
            self.agent = Dosaku()

        _app = FastAPI()

        @_app.post('/list-commands')
        def list_commands():
            return {'commands': self.agent.commands()}

        @_app.post('/chat')
        def chat(payload: ChatInput):
            response = self.agent.chat(text=payload.text)
            return {'sender': response.sender, 'text': response.text}

        @_app.post('/text-to-image')
        def text_to_image(payload: TextToImageInput):
            image = self.agent.text_to_image(prompt=payload.prompt)
            return {'prompt': payload.prompt, 'image': pil_to_ascii(image)}

        @_app.post('/transcribe-interview')
        def transcribe_interview(payload: TranscribeInterviewInput):
            pass

        @_app.post('/voices')
        def voices():
            return {'voices': self.agent.voices()}

        @_app.post('/voice')
        def voice(payload: VoiceInput):
            return {'voice': payload.voice}

        return _app

    @classmethod
    def connection(cls, host):
        return Connection(host)


def app():
    server = Server()
    return server.app()
