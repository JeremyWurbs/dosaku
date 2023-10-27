from abc import ABC, abstractmethod
from typing import Dict, List

from dosaku import Actor, task_hub, NameAttributeNotFound


class Task(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @classmethod
    def api(cls) -> List[str]:
        api_concrete_methods = getattr(cls, 'api_concrete_methods', list())
        return api_concrete_methods + list(cls.__abstractmethods__)

    @classmethod
    def docs(cls) -> Dict[str, str]:
        doc = {cls.name: cls.__doc__}
        for attr in cls.api():
            try:  # TODO: Sometimes <local> _Task objects try to register themselves with api's they don't have. Fix.
                doc[attr] = getattr(cls, attr).__doc__
            except:
                pass
        return doc

    @classmethod
    def register_task(cls):
        if not isinstance(cls.name, str):
            raise NameAttributeNotFound(
                f'A unique string name attribute is required, but was not found for task {cls}. Make sure '
                f'to add a name attribute to your task.')
        task_hub.register_task(task=cls.name, api=cls.api(), docs=cls.docs())

    @classmethod
    def create(cls, name: str, api: Dict[str, str]):
        class _Task(Task):
            api_concrete_methods = list(api.keys())

            def __init__(self, name):
                self._name = name

            @property
            def name(self):
                return self._name

        _task = _Task(name)
        for action_name, doc in api.items():
            action = Actor(doc=doc)
            _task.__setattr__(action_name, action)

        return _task
