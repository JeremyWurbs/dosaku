from dataclasses import dataclass, field
from PIL.Image import Image
from typing import List, Optional

from dosaku.types import Audio


@dataclass
class Chapter:
    text: Optional[str] = None
    summary: Optional[str] = None
    illustrations: List[Image] = field(default_factory=list)
    audio: Optional[Audio] = None

    @property
    def num_words(self):
        return len(self.text.split(' '))
