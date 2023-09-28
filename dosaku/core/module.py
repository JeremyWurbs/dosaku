from abc import ABC, abstractmethod

from dosaku import task_hub, module_manager


class Module(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @classmethod
    def register_module(cls):
        module_manager.register_builder(cls.name, cls)

    @classmethod
    def register_task(cls, task: str):
        cls.register_module()
        task_hub.register_module(cls, tasks=task)
