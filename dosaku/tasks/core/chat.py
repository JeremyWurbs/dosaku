"""Interface for a generic conversation Chat task."""
from dataclasses import dataclass, field
from PIL.Image import Image
from typing import List

import numpy as np


class Chat:
    """Interface for a generic conversational chatbot.

    A chat module is not obligated to support streaming, but if stream=True is passed in on init and the module does not
    support streaming, it must raise an OptionNotSupported exception.

    Args:
        stream: Whether to stream messages.
    """

    @dataclass
    class Message:
        sender: str
        message: str
        images: List[Image] = field(default_factory=list)
        audio: List[np.ndarray] = field(default_factory=list)

    name = 'Chat'
