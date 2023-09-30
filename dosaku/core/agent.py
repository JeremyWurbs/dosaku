from typing import Dict, List, Optional, Union

from dosaku import Config, Task, task_hub, module_manager
from dosaku.core.action import Action
from dosaku import tasks  # Do not remove: allows all tasks in the dosaku.tasks namespace to register themselves
from dosaku import modules  # Do not remove: allows all modules in the dosaku.modules namespace to register themselves


class Agent:
    config = Config()
    task_hub = task_hub
    module_manager = module_manager

    def __init__(self, enable_services=False):
        self._known_tasks: Dict[str: List[str]] = dict()
        self._allow_services = enable_services

    @classmethod
    def register_task(cls, task: Task):
        cls.task_hub.register_task(task)

    @classmethod
    def api(cls, task: str):
        return cls.task_hub.api(task)

    @classmethod
    def doc(cls, task: str, action: Optional[str] = None):
        return cls.task_hub.doc(task=task, action=action)

    @property
    def learnable_tasks(self):
        return list(self.task_hub.tasks.keys())

    @property
    def tasks(self):
        return list(self._known_tasks.keys())

    def registered_modules(self, task: str):
        return self.task_hub.registered_modules(task)

    def loaded_modules(self):
        return self.module_manager.modules

    def enable_services(self):
        self._allow_services = True

    def disable_services(self):
        self._allow_services = False

    @property
    def services_enabled(self):
        return self._allow_services

    def learn(self, task: Union[str, Task], module: Optional[str] = None, force_relearn=False, **kwargs):
        if isinstance(task, Task):
            task = task.name

        if module is None:
            modules = self.task_hub.registered_modules(task)
            if modules is None:
                raise ValueError(f'There are no known modules which have registered the task {task}.')
            module = modules[0]

        print(f'Attemping to learn {task} via the module {module}.')
        try:
            self.module_manager.load_module(
                module, force_reload=force_relearn, allow_services=self._allow_services, **kwargs)
        except RuntimeError as err:
            raise err

        setattr(self, task, Action())
        for method in self.task_hub.api(task):
            module_attr = self.module_manager.get_module_attr(module, method)
            setattr(getattr(self, task), method, module_attr)
        self._known_tasks[task] = self.task_hub.api(task)
