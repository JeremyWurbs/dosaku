"""Interface for writing a new module."""
from abc import abstractmethod

from dosaku import Task


class WriteModule(Task):
    """Abstract interface class for a task to write modules."""
    name = 'WriteModule'

    @abstractmethod
    def write_module(self, context: str, module_reqs: str, examples: str, **kwargs):
        raise NotImplementedError


WriteModule.register_task()
