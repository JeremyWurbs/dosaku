class ActionDoesNotExist(AttributeError):
    """Raised when the current resource does not have the requested action attribute."""


class CodingError(RuntimeError):
    """Raised when generated code fails to pass an assertion or quality check."""


class ExecutorPermissionRequired(PermissionError):
    """Raised when the current resource requires Executor permissions, but does not have it."""


class InterpreterError(Exception):
    """Raised when capturing a generic exception from exec."""


class ModuleForTaskNotFound(ModuleNotFoundError):
    """Raised when trying to instantiate a Task but no suitable Module is found."""


class NameAttributeNotFound(NotImplementedError):
    """Raised when a resource does not have a name attribute."""


class OptionNotSupported(NotImplementedError):
    """Raised when an option is passed to a resource that it does not support."""


class ServicePermissionRequired(PermissionError):
    """Raised when the current resource requires Service permissions, but does not have it."""
