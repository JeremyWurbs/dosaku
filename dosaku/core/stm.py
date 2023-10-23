import copy
from typing import List, Union

from dosaku import Executor, InterpreterError


class ShortTermModule(Executor):
    """Module that can be initiated dynamically.

    A ShortTermModule is an Executor that runs dynamically generated code.

    Note that the module will be deleted when it loses scope or the application ends. To use a given ShortTermModule in
    the future, save it as a standard Module.

    Args:
        name: A unique module name to give the module.
        code: The code to run when the module is called.
        actions: List of actions the module may do. Actions must be methods defined in the code's global scope.

    Example::

        from dosaku import Agent, ShortTermModule

        agent = Agent(enable_services=True, enable_executors=True)
        agent.learn('Coder')

        code = agent.Coder(
            'Write two methods, gcd and collatz. The gcd method should take two integers and compute their greatest '
            'common denominator. The collatz method should take a single integer and return is 3n+1 collatz path.')
        stm = ShortTermModule(name='HelperMathMethods', code=code, actions=['gcd', 'collatz'])

        print(code)
        \"\"\"
        # Here is the Python code for the gcd and collatz functions
        def gcd(a, b):
            # Finding the greatest common denominator
            while(b):
                a, b = b, a % b
            return a
        def collatz(n):
            sequence = [n]
            # Generating the collatz sequence
            while n != 1:
                if n % 2 == 0: # n is even
                    n = n / 2
                else: # n is odd
                    n = 3 * n + 1

                sequence.append(n)
            return sequence
        \"\"\"

        stm.gcd(10, 15)  # 5
        stm.collatz(21)  # [21, 64, 32, 16, 8, 4, 2, 1]

    """
    name = 'ShortTermModule'

    def __init__(self, name: str, code: str, actions: Union[str, List[str]]):
        self.name = name
        self.code = code
        if isinstance(actions, str):
            actions = [actions]

        # Put the code into the (__init__) locals namespace
        result, err = self.exec(self.code, globals=globals())

        if len(err) > 0:
            raise InterpreterError(err)

        for action in actions:
            action_copy = copy.copy(action)  # capture the action into the _Actor namespace

            class _Actor:
                action = action_copy

                @classmethod
                def __call__(cls, *args, **kwargs):
                    return globals()[cls.action](*args, **kwargs)

            setattr(self, action_copy, _Actor())

    def __call__(self, method_name: str, *args, **kwargs):
        return getattr(self, method_name)(*args, **kwargs)
