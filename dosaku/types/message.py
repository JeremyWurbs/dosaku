from dataclasses import dataclass, field
from PIL.Image import Image
from typing import List, Optional

import numpy as np


@dataclass
class Message:
    sender: Optional[str] = None
    text: Optional[str] = None
    images: List[Image] = field(default_factory=list)
    audio: List[np.ndarray] = field(default_factory=list)
