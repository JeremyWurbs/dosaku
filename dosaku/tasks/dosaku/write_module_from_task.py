"""Interface for writing a new module from an existing task."""
from abc import abstractmethod

from dosaku import Task


class WriteModuleFromTask(Task):
    """Abstract interface class for a task to write modules from pre-existing tasks."""
    name = 'WriteModuleFromTask'

    @abstractmethod
    def write_module_from_task(
            self,
            task_filename: str,
            module_reqs: str = None,
            write_to_file: bool = False,
            filename: str = None,
            **kwargs
    ) -> str:
        raise NotImplementedError


WriteModuleFromTask.register_task()
