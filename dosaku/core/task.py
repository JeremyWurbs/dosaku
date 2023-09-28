from abc import ABC, abstractmethod
from typing import List

from dosaku import task_hub


class Task(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @classmethod
    def api(cls) -> List[str]:
        return list(cls.__abstractmethods__)

    @classmethod
    def register_task(cls):
        task_hub.register_task(task=cls.name, api=cls.api())
