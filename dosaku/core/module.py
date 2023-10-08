from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Union

from dosaku import Task, task_hub, module_manager


class Module(ABC):
    api_task_actions: Dict[str, str] = dict()
    dependencies: List[str] = list()  # List of module dependencies

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    def is_service(self):
        return False

    @classmethod
    def api(cls):
        return cls.api_task_actions

    @classmethod
    def docs(cls) -> Dict[str, str]:
        doc = {cls.name: cls.__doc__}
        for attr in cls.api():
            doc[attr] = getattr(cls, attr).__doc__
        return doc

    @classmethod
    def register_action(cls, func: Union[str, Callable], doc: Optional[str] = None):
        if isinstance(func, Callable):
            func = func.__name__
            if doc is None:
                doc = func.__doc__
        cls.api_task_actions[func] = doc

    @classmethod
    def register_module(cls):
        module_manager.register_builder(module=cls.name, builder=cls, dependencies=cls.dependencies)

    @classmethod
    def register_task(cls, task: str):
        cls.register_module()
        if task == cls.__name__:  # Module is acting as both Task & Module. Register a new task derived from the Module.
            new_task = Task.create(name=task, api=cls.api())
            task_hub.register_task(task=new_task.name, api=new_task.api(), docs=new_task.docs())
        task_hub.register_module(cls, tasks=task)
