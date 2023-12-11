from typing import List

from dosaku.types import Message


class ChatHistory:
    def __init__(self):
        self.history: List[Message] = []

    def add_message(self, message: Message):
        self.history.append(message)

    def reset(self):
        self.history = []
