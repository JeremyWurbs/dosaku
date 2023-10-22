class ExecutorPermissionRequired(PermissionError):
    """Raised when the current resource requires Executor permissions, but does not have it."""


class InterpreterError(Exception):
    """Raised when capturing a generic exception from exec."""


class ModuleForTaskNotFound(ModuleNotFoundError):
    """Raised when trying to instantiate a Task but no suitable Module is found."""


class ServicePermissionRequired(PermissionError):
    """Raised when the current resource requires Service permissions, but does not have it."""
