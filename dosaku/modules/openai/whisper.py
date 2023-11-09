from typing import List, Optional, Tuple

import numpy as np
from transformers import pipeline


class Whisper:
    """OpenAI's speech-to-text Whisper model.

    Args:
        spellcheck: CURRENTLY NOT SUPPORTED. Whether to spellcheck the output text before returning it.
        spellcheck_model: The model to use for spellchecking the output.
        key_terms: A list of key terms. The spellchecker will be prompted with these terms to know their spelling.

    Example::

        import gradio as gr
        from dosaku.modules import Whisper

        whisper = Whisper()
        demo = gr.Interface(
            whisper.gradio_stream,
            ["state", gr.Audio(source="microphone", streaming=True)],
            ["state", "text"],
            live=True
        )
        demo.launch()

    """
    name = 'Whisper'

    def __init__(self, spellcheck: bool = False, spellcheck_model: Optional[str] = None, key_terms: List[str] = None):
        self.model = pipeline("automatic-speech-recognition", model="openai/whisper-base.en")
        self.audio_stream = None
        self._text = None
        self.spellchecker = None
        if spellcheck:
            raise NotImplementedError
            self.spellchecker = Spellchecker(model=spellcheck_model, key_terms=key_terms)

    def text(self, corrected_text: Optional[str] = None):
        """Combined setter and getter for obtaining the transcribed text.

        The text method may be called after any transcribe method (transcribe, stream, gradio_stream) to return the
        transcribed text up to that point. If following a call to transcribe, text() will return the transcription of
        the most recent transcribe call; if following a streaming call, text() will return the entire transcription.

        If using an external spellchecker, a corrected_text argument may be passed in, in which case the internal text
        store will be overwritten. Note that any calls to a transcribe method will overwrite the internal text store,
        and thus will overwrite the corrected_text passed in.

        Args:
            corrected_text (optional): The corrected (grammar, spellchecked, etc.) text of the last transcribe call.

        Returns:
            The current internal text store.
        """
        if corrected_text is not None:
            self._text = corrected_text
        return self._text

    def transcribe(self, audio: Tuple[int, np.ndarray]) -> str:
        """Transcribe the given audio data.

        The audio data should be a tuple of the form (int, np.ndarray), where the first element is the sampling rate of
        the audio, and the second element is the actual audio data.

        Args:
            audio: The audio data to transcribe.

        Returns:
            The transcribed text.
        """
        sr, y = audio
        y = y.astype(np.float32)
        y /= np.max(np.abs(y))

        self._text = self.model({"sampling_rate": sr, "raw": y})["text"]
        if self.spellchecker:
            self._text = self.spellchecker(self.text())

        return self.text()

    def stream(self, new_chunk: Tuple[int, np.ndarray]) -> str:
        """Transcribe the given audio stream.

        The audio data should be a tuple of the form (int, np.ndarray), where the first element is the sampling rate of
        the audio, and the second element is the actual audio data. For the stream method, the audio given should only
        be the new chunk of audio not yet processed. The Whisper object will concatenate the new audio chunk and return
        the transcribed text of the entire audio passed in.

        Args:
            new_chunk: The new chunk of the audio stream to process.

        Returns:
            The entire transcribed text up to that point. Use reset_stream to reset the transcribed text.
        """
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

    def gradio_stream(self, stream, new_chunk):
        """Transcribe the given audio stream using the Gradio signature format.

        The gradio Interface class expects the stream method to accept (and return) the entire audio stream in addition
        to the new audio chunk. As the Whisper class manages updating the stream with every new chunk, the extra stream
        argument is superfluous, and stream() will be used under the hood.

        Args:
            stream: The entire audio stream, up to but not including the new_chunk.
            new_chunk: The new chunk of the audio stream to process.

        Returns:
            The entire transcribed text up to that point. Use reset_stream to reset the transcribed text.
        """
        return stream, self.stream(new_chunk)

    def reset_stream(self):
        """Reset the internal audio data store.

        Call reset_stream when you are streaming audio data and want to start a new transcribed message.
        """
        self.audio_stream = None
