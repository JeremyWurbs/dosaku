import base64
from io import BytesIO
from typing import Optional

import numpy as np
import pydub
from pydub import AudioSegment


class Audio:
    def __init__(
            self,
            sample_rate: Optional[int] = None,
            data: Optional[np.ndarray] = None,
            filename: Optional[str] = None,
            normalized: bool = False):
        self.sample_rate = sample_rate
        self.data = data
        if filename is not None:
            self.load(filename, normalized=normalized)

    def load(self, filename, normalized=False):
        """MP3 to numpy array"""
        audio = AudioSegment.from_mp3(filename)
        _tmp = Audio.from_audiosegment(audio, normalized=normalized)
        self.data = _tmp.data
        self.sample_rate = _tmp.sample_rate

    def write(self, filename: str, normalized=False):
        audio = self.to_audiosegment(normalized)
        audio.export(filename, format='mp3', bitrate='320k')

    def to_audiosegment(self, normalized=False):
        """numpy array to MP3"""
        channels = 2 if (self.data.ndim == 2 and self.data.shape[1] == 2) else 1
        if normalized:  # normalized array - each item should be a float in [-1, 1)
            audio_data = np.int16(self.data * 2 ** 15)
        else:
            audio_data = np.int16(self.data)
        audio = pydub.AudioSegment(audio_data.tobytes(), frame_rate=self.sample_rate, sample_width=2, channels=channels)
        return audio

    def to_bytes(self, normalized=False) -> bytes:
        audio = self.to_audiosegment(normalized)
        buffer = BytesIO()
        audio.export(buffer, format='mp3')
        return buffer.getvalue()

    def to_ascii(self, normalized=False) -> str:
        audio = self.to_bytes(normalized=normalized)
        converter = base64.b64encode(audio)
        return converter.decode('ascii')

    @classmethod
    def from_audiosegment(cls, audio: AudioSegment, normalized=False):
        audio_data = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            audio_data = audio_data.reshape((-1, 2))
        if normalized:
            sample_rate = audio.frame_rate
            data = np.float32(audio_data) / 2 ** 15
        else:
            sample_rate = audio.frame_rate
            data = audio_data
        return Audio(sample_rate=sample_rate, data=data, normalized=normalized)

    @classmethod
    def from_bytes(cls, bytes: BytesIO):
        audio = pydub.AudioSegment.from_mp3(bytes)
        return Audio.from_audiosegment(audio)

    @classmethod
    def from_ascii(cls, ascii: str):
        return Audio.from_bytes(BytesIO(base64.b64decode(ascii)))
