from __future__ import annotations
from abc import abstractmethod
from typing import List, TYPE_CHECKING

from dosaku import Task
if TYPE_CHECKING:
    from dosaku.logic import Context


class LogicActor(Task):
    name = 'LogicActor'

    @abstractmethod
    def act_on_context(self, context: Context) -> Context:
        raise NotImplementedError


class LogicEvaluator(Task):
    name = 'LogicEvaluator'

    @abstractmethod
    def evaluate_from_context(self, context: Context, labels: List[str]) -> str:
        raise NotImplementedError


LogicActor.register_task()
LogicEvaluator.register_task()
