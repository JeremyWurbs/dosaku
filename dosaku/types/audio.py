from typing import Optional

import numpy as np
import pydub


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
        audio = pydub.AudioSegment.from_mp3(filename)
        audio_data = np.array(audio.get_array_of_samples())
        if audio.channels == 2:
            audio_data = audio_data.reshape((-1, 2))
        if normalized:
            self.sample_rate = audio.frame_rate
            self.data = np.float32(audio_data) / 2**15
        else:
            self.sample_rate = audio.frame_rate
            self.data = audio_data

    def write(self, filename: str, normalized=False):
        """numpy array to MP3"""
        channels = 2 if (self.data.ndim == 2 and self.data.shape[1] == 2) else 1
        if normalized:  # normalized array - each item should be a float in [-1, 1)
            audio_data = np.int16(self.data * 2 ** 15)
        else:
            audio_data = np.int16(self.data)
        audio = pydub.AudioSegment(audio_data.tobytes(), frame_rate=self.sample_rate, sample_width=2, channels=channels)
        audio.export(filename, format="mp3", bitrate="320k")
