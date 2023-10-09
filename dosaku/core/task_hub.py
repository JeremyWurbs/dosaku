from __future__ import annotations
from typing import Dict, List, Optional, Union, TYPE_CHECKING

from dosaku import TaskInfo
if TYPE_CHECKING:
    from dosaku import Module


class TaskHub:
    def __init__(self):
        self._tasks_info: Dict[str, TaskInfo] = {}

    @property
    def tasks(self):
        return self._tasks_info

    def api(self, task: str):
        if task not in self.tasks:
            raise ValueError(f'A task with the name {task} has not been registered.')
        return self.tasks[task].api

    def doc(self, task: str, action: Optional[str] = None) -> str:
        if action is None:
            return self.tasks[task].docs[task]
        else:
            return self.tasks[task].docs[action]

    def registered_modules(self, task: str) -> List[str]:
        if task not in self.tasks:
            raise ValueError(f'A task with the name {task} has not been registered.')
        return self.tasks[task].modules

    def register_task(self, task: str, api: List[str], docs: Optional[Dict[str, str]] = None):
        print(f'Attempting to register a task named {task}.')
        if task in self.tasks:
            raise ValueError(f'A task with the name {task} has already been registered. It will not be registered again.')
        self._tasks_info[task] = TaskInfo(name=task, api=api, docs=docs)

    def register_module(self, module: Union[str, Module], tasks: Union[str, List[str]]):
        print(f'Attempting to register module {module}.')
        if isinstance(tasks, str):
            tasks = [tasks]
        for task in tasks:
            if self.tasks.get(task) is None:
                raise ValueError(f'A Task with the name {task} has not been registered. Register tasks before modules.')
            self.tasks[task].register_module(module)


task_hub = TaskHub()
