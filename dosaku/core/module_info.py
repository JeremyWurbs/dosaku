from dataclasses import dataclass
from typing import Callable, List, Optional


@dataclass
class ModuleInfo:
    builder: Optional[Callable] = None
    dependencies: Optional[List[str]] = None
