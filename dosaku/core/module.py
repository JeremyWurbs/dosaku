from __future__ import annotations
from abc import ABC, abstractmethod
import io
import sys
from typing import Callable, Dict, List, Optional, Tuple, Union

from dosaku import Task, task_hub, module_manager


class Module(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    def is_service(self) -> bool:
        return False

    @property
    def is_executor(self) -> bool:
        return False

    @classmethod
    def exec(cls, code: str) -> Tuple[str, str]:
        """Runs the given python code.

        This method uses Python's exec to run a dynamically created program. It is expected that this code is being
        dynamically generated by an AI agent, and that it is not yet ascertained if this code will even run without
        errors.

        Args:
            code: The python code to run.

        Returns:
            A tuple of the form (code output, any errors generated).

        .. warning::
            Do not run any code you do not trust. Do not allow executors to run code on your behalf that you do not
            trust. You are ultimately responsible for whatever code is run on your behalf, regardless of its
            output or consequences.

        """
        if cls.is_executor:
            # create file-like string to capture output
            codeOut = io.StringIO()
            codeErr = io.StringIO()

            # capture output and errors
            sys.stdout = codeOut
            sys.stderr = codeErr

            exec(code)

            # restore stdout and stderr
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            return codeOut.getvalue(), codeErr.getvalue()

        else:
            raise ValueError(f'Module {cls.name} is not an executor, but tried to run exec. Only executors are allowed '
                             f'to run exec.')

    @classmethod
    def api(cls) -> Optional[Dict[str, str]]:
        return getattr(cls, 'api_task_actions', None)

    @classmethod
    def docs(cls) -> Dict[str, str]:
        doc = {cls.name: cls.__doc__}
        for attr in cls.api():
            doc[attr] = getattr(cls, attr).__doc__
        return doc

    @classmethod
    def register_action(cls, func: Union[str, Callable], doc: Optional[str] = None):
        if getattr(cls, 'api_task_actions', None) is None:
            cls.api_task_actions: Dict[str, str] = dict()

        if isinstance(func, Callable):
            func = func.__name__
            if doc is None:
                doc = func.__doc__
        cls.api_task_actions[func] = doc

    @classmethod
    def register_dependency(cls, dependency: Union[str, Module]):
        if isinstance(dependency, Module):
            dependency = dependency.name
        if getattr(cls, '_dependencies', None) is None:
            cls._dependencies: List[str] = list()
        cls._dependencies.append(dependency)

    @classmethod
    @property
    def dependencies(cls):
        return getattr(cls, '_dependencies', list())

    @classmethod
    def register_module(cls):
        module_manager.register_builder(module=cls.name, builder=cls, dependencies=getattr(cls, '_dependencies', list()))

    @classmethod
    def register_task(cls, task: str):
        cls.register_module()
        if task == cls.__name__:  # Module is acting as both Task & Module. Register a new task derived from the Module.
            new_task = Task.create(name=task, api=cls.api())
            task_hub.register_task(task=new_task.name, api=new_task.api(), docs=new_task.docs())
        task_hub.register_module(cls, tasks=task)
