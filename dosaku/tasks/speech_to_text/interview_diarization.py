"""Interface for an Interview Diarization task."""
from abc import abstractmethod

from dosaku import Task


class InterviewDiarization(Task):
    """Abstract interface class for interview transcription task including diarization (speaker identification).

    In an interview context, there is one interviewer and one interviewee.
    """
    name = 'InterviewDiarization'

    @abstractmethod
    def transcribe_interview(self, audio_file: str) -> str:
        """Return transcribed text from interview audio file, including speaker identification.

        The returned text should include proper grammar, punctuation, and speaker identification, as well as removing
        superfluous "ums" and other filler words.

        Args:
            audio_file: Filename to mp3 or equivalent audio file.

        Returns:
            The transcribed text.
        """
        raise NotImplementedError
