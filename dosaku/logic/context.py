from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from dosaku.tasks import Chat


@dataclass
class Context:
    conversation: Optional[Chat] = None
    short_term_memory: Optional[Any] = None

    @property
    def instruction(self) -> str:
        return self.conversation.history()[-1].message
