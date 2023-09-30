from abc import ABC, abstractmethod
from typing import Dict, List

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
    def docs(cls) -> Dict[str, str]:
        doc = {cls.name: cls.__doc__}
        for attr in cls.api():
            doc[attr] = getattr(cls, attr).__doc__
        return doc

    @classmethod
    def register_task(cls):
        task_hub.register_task(task=cls.name, api=cls.api(), docs=cls.docs())
