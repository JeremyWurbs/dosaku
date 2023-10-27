from typing import List, Optional

import numpy as np
from transformers import pipeline

from dosaku import Module
from dosaku.modules import Spellchecker


class Whisper(Module):
    """OpenAI's speech-to-text Whisper model."""
    name = 'Whisper'

    def __init__(self, spellcheck: bool = False, spellcheck_model: Optional[str] = None, key_terms: List[str] = None):
        self.model = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
        self.audio_stream = None
        self._text = None
        self.spellchecker = None
        if spellcheck:
            self.spellchecker = Spellchecker(model=spellcheck_model, key_terms=key_terms)

    def text(self, corrected_text: Optional[str] = None):
        if corrected_text is not None:
            self._text = corrected_text
        return self._text

    def transcribe(self, audio) -> str:
        sr, y = audio
        y = y.astype(np.float32)
        y /= np.max(np.abs(y))

        self._text = self.model({"sampling_rate": sr, "raw": y})["text"]
        if self.spellchecker:
            self._text = self.spellchecker(self.text())

        return self.text()

    def stream(self, new_chunk) -> str:
        sr, y = new_chunk
        y = y.astype(np.float32)
        y /= np.max(np.abs(y))

        if self.audio_stream is not None:
            self.audio_stream = np.concatenate([self.audio_stream, y])
        else:
            self.audio_stream = y

        self._text = self.model({'sampling_rate': sr, 'raw': self.audio_stream})['text']
        if self.spellchecker:
            self._text = self.spellchecker(self.text())

        return self.text()

    def reset_stream(self):
        self.audio_stream = None


Whisper.register_task('SpeechToText')
Whisper.register_task('RealtimeSpeechToText')
