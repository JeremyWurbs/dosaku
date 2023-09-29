from abc import ABC, abstractmethod

from dosaku import task_hub, module_manager


class Module(ABC):
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    @property
    def is_service(self):
        return False

    @classmethod
    def register_module(cls):
        module_manager.register_builder(module=cls.name, builder=cls, is_service=cls.is_service)

    @classmethod
    def register_task(cls, task: str):
        cls.register_module()
        task_hub.register_module(cls, tasks=task)
