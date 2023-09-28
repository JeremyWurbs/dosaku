from typing import Callable, Dict, List, Union

from dosaku import TaskInfo


class TaskHub:
    def __init__(self):
        self._tasks: Dict[str, TaskInfo] = {}

    @property
    def tasks(self):
        return self._tasks

    def api(self, task: str):
        if task not in self.tasks:
            raise ValueError(f'A task with the name {task} has not been registered.')
        return self.tasks[task].api

    def registered_modules(self, task: str) -> List[str]:
        if task not in self.tasks:
            raise ValueError(f'A task with the name {task} has not been registered.')
        return self.tasks[task].modules

    def register_task(self, task: str, api: List[Callable]):
        print(f'Attempting to register a task named {task}.')
        if task in self.tasks:
            raise ValueError(f'A task with the name {task} has already been registered. It will not be registered again.')
        self._tasks[task] = TaskInfo(name=task, api=api)

    def register_module(self, module: str, tasks: Union[str, List[str]]):
        print(f'Attempting to register a module named {module}.')
        if isinstance(tasks, str):
            tasks = [tasks]
        for task in tasks:
            if self.tasks.get(task) is None:
                raise ValueError(f'A Task with the name {task} has not been registered. Register tasks before modules.')
            self.tasks[task].register_module(module)


task_hub = TaskHub()
