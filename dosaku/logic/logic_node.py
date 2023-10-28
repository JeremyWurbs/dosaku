from typing import Any, Callable, List, Optional, Tuple, Union

from dosaku.logic import Context
from dosaku.utils import ifnone
from dosaku.tasks import LogicActor, LogicEvaluator


class LogicNode:
    """Logic Node

    Args:
        label: The label for this node. Will be used by evaluators to determine when to run this node.
        action: The action to run for this node. If given, must accept and return a Context.
        evaluator: Evaluator to run for this node. If given, must accept (Context, children_labels) and return a label.
        children: Child nodes which may be run next, determined by the output of the evaluator.
    """
    def __init__(
            self,
            label: str,
            action: Optional[Union[Callable, LogicActor]] = None,
            evaluator: Optional[Union[Callable, LogicEvaluator]] = None,
            children: Optional[List['LogicNode']] = None
    ):
        self.label = label
        self.action = action
        self.evaluator = evaluator
        self._children = ifnone(children, default=dict())

    @property
    def children(self):
        return list(self._children.values())

    @property
    def children_labels(self):
        return list(self._children.keys())

    def add_child(self, node: 'LogicNode'):
        self._children[node.label] = node

    def run(self, context: Context) -> Tuple[Any, Optional['LogicNode']]:
        """Run the logic node.

        Running a logic node will do the following:

        1. Run the node's action, if not None.
        2. Run the node's evaluator, if not None.
        3. Return the updated context and next node to run.

        Args:
            context: The input logic context to use.

        Returns:
            A tuple of the form (updated_context: Context, next_node: Optional[LogicNode]). The next_node will be None
            if no child node was selected to run next.
        """
        context = self.act(context)
        next_node = self.evaluate(context)

        return context, next_node

    def act(self, context: Context) -> Context:
        if self.action is None:
            return context
        elif isinstance(self.action, Callable):
            return self.action(context)
        else:  # LogicActor
            return self.action.act_on_context(context)

    def evaluate(self, context: Context) -> Optional['LogicNode']:
        if self.evaluator is None:
            return None
        elif isinstance(self.evaluator, Callable):
            next_node = self.evaluator(context=context, labels=self.children_labels)
        else:  # LogicEvaluator
            next_node = self.evaluator.evaluate_from_context(context=context, labels=self.children_labels)

        if next_node is not None:
            next_node = self._children[next_node]

        return next_node

    def __call__(self, context: Context) -> Tuple[Any, Optional['LogicNode']]:
        return self.run(context)
