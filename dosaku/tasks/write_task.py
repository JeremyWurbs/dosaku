"""Interface for writing a new module."""
from abc import abstractmethod

from dosaku import Task


class WriteTask(Task):
    """Abstract interface class for a task to write tasks."""
    name = 'WriteTask'

    @abstractmethod
    def write_task(self, context: str, module_reqs: str, examples: str, **kwargs):
        raise NotImplementedError


WriteTask.register_task()
