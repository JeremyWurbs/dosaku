from pydantic import BaseModel


class ChatInput(BaseModel):
    text: str


class TextToImageInput(BaseModel):
    prompt: str


class TranscribeInterviewInput(BaseModel):
    audio_file: str
    interviewer: str
    interviewee: str


class VoiceInput(BaseModel):
    voice: str
