from typing import List, Optional, Union

from dosaku import Config, Executor, Service, ShortTermModule
from dosaku.modules import OpenAIChat
from dosaku.utils import ifnone, clean_code


class Coder(Executor, Service):
    """Iteratively tests and writes code.

    As Coder is both an Executor and a Service, it is highly recommended to use Coder through an Agent to make sure
    the proper permissions are given.
    """
    name = 'Coder'
    config = Config()
    default_system_prompt = (
        'You are an expert python developer, tasked with writing code to match a given description. Your code should '
        'be able to run directly in a python interpreter. That is, DO comment all of your code, but DO NOT add any '
        'explanatory text or markdown code, such as ```python. Any explanatory code MUST be written as python '
        'comments.\n'
        '\n'
        'After you write code it will be run. If there are errors you will be given the errors. You should respond by '
        'rewriting ALL of the code with the errors corrected.\n'
    )
    determine_actions_prompt = (
        'You are an expert python developer, tasked with determining the user API for a given piece of code. You '
        'will be given a user conversation with an accompanying piece of code. You should respond with a python '
        'List[str] containing the names of the main API methods. The methods you return must exist in the given code.'
        'It is possible that extra methods are present which are only used as helper methods, in which case you should '
        'not return them as part of the API. For example: \n'
        '\n'
        'User: Write the following set of python methods, use any extra helper methods as necessary: (1) accepts an '
        'integer and returns whether it is prime; (2) accepts an integer and returns its collatz 3n+1 path; (3) '
        'accepts two integers and an optional length parameter defaulting to 20 and returns the fibinacci sequence (of '
        'the optional parameter length) starting with the two integers.\n'
        '\n'
        'Assistant: ```python\n'
        'def is_prime(n):\n'
        '    if n <= 1:\n'
        '        return False\n'
        '    if n == 2:\n'
        '        return True\n'
        '    if n % 2 == 0:\n'
        '        return False\n'
        '    i = 3\n'
        '    while i * i <= n:\n'
        '        if n % i == 0:\n'
        '            return False\n'
        '        i += 2\n'
        '    return True\n'
        '\n'
        'def collatz(n):\n'
        '    sequence = [n]\n'
        '    while n != 1:\n'
        '        if n % 2 == 0:\n'
        '            n = n // 2\n'
        '        else:\n'
        '            n = 3 * n + 1\n'
        '        sequence.append(n)\n'
        '    return sequence\n'
        '\n'
        'def fibonacci(n1, n2, length=20):\n'
        '    sequence = [n1, n2]\n'
        '    while len(sequence) < length:\n'
        '        sequence.append(sequence[-1] + sequence[-2])\n'
        '    return sequence\n'
        '```\n'
        'User: Return the API for the previous conversation:\n'
        '\n'
        'You should respond:\n'
        '\n'
        '[\'is_prime\', \'collatz\', \'fibonacci\']'
    )
    determine_name_prompt = (
        'You are an expert python developer, tasked with writing class names for a given API. The API will contain a '
        'set of Python methods implementing a request from a user. You should respond with the Python class name that '
        'should contain the given methods. For example:\n'
        '\n'
        'User: Write the following set of python methods, use any extra helper methods as necessary: (1) accepts an '
        'integer and returns its collatz 3n+1 path; (2) accepts two integers and an optional length parameter '
        'defaulting to 20 and returns the fibinacci sequence (of the optional parameter length) starting with the two '
        'integers.\n'
        '\n'
        'Assistant: ```python\n'
        'def collatz(n):\n'
        '    sequence = [n]\n'
        '    while n != 1:\n'
        '        if n % 2 == 0:\n'
        '            n = n // 2\n'
        '        else:\n'
        '            n = 3 * n + 1\n'
        '        sequence.append(n)\n'
        '    return sequence\n'
        '\n'
        'def fibonacci(n1, n2, length=20):\n'
        '    sequence = [n1, n2]\n'
        '    while len(sequence) < length:\n'
        '        sequence.append(sequence[-1] + sequence[-2])\n'
        '    return sequence\n'
        '```\n'
        'User: Return the API for the previous conversation:\n'
        '\n'
        'Assistant: [\'collatz\', \'fibonacci\']\n'
        '\n'
        'User: Write the API class name for the previous conversation:\n'
        '\n'
        'You should respond:\n'
        ''
        'MathSequences'
    )

    def __init__(self, model: str = None):
        super().__init__()
        self.model = ifnone(model, default=self.config['OPENAI']['DEFAULT_MODEL'])

    def write_code(
            self,
            description: str,
            max_tries: Optional[int] = None,
            return_intermediate_tries: bool = False
    ) -> Union[str, List[str]]:
        """Writes code based on the given description.

        Args:
            description: A description of the code to write.
            max_tries: The maximum number of tries before returning. If not given, defaults to the value in config.ini.
            return_intermediate_tries: Whether to return the intermediate tries

        Returns:
            The generated code. If return_intermediate_tries is False (the default), the code will be returned as a
            string. If return_intermediate_tries is True, the code will be returned as a list of str, where code[0] was
            the first try and code[-1] the last. In this case, the "final" code should be taken as this last value,
            code[-1].

        Example::

            from dosaku import Agent

            agent = Agent(enable_services=True, enable_executors=True)
            agent.learn('Coder')
            code = agent.Coder('Write a method that takes two integers and returns their greatest common denominator.")
        """
        max_tries = ifnone(max_tries, default=self.config['DOSAKU'].getint('CODER_MAX_TRIES'))

        conversation = OpenAIChat(system_prompt=self.default_system_prompt, model=self.model)
        code = conversation.message(f'Write python code to match the following requirements: {description}')
        code = clean_code(code)
        intermediate_tries = [code]

        num_tries = 0
        while num_tries < max_tries:
            result, err = self.exec(code, globals=globals())
            if err != '':
                code = conversation.message(f'Your code received the following error: {err}\n\nRewrite your code.')
                code = clean_code(code)
                num_tries += 1
                if return_intermediate_tries:
                    intermediate_tries.append(code)
            else:
                break

        if return_intermediate_tries:
            return intermediate_tries
        else:
            return code

    def create_stm(
            self,
            code: Union[str, OpenAIChat],
            name: Optional[str] = None,
            actions: Optional[Union[str, List[str]]] = None
    ) -> ShortTermModule:
        """Create a ShortTermModule based on the given code.

        If the name or actions are not given, they will be inferred from the code itself.

        Args:
            code: The code to turn into a ShortTermModule.
            name: The name of returned module.
            actions: The list of module actions.

        Returns:
            A ShortTermModule that wraps the given code.

        Example::

            from dosaku.agents import Dosaku

            agent = Dosaku(enable_services=True, enable_executors=True, stream_chat=False)
            agent.learn('Coder')

            desc = (
                'Write the following set of python methods, use any extra helper methods as necessary: (1) accepts an '
                'integer and returns whether it is prime; (2) accepts an integer and returns its collatz 3n+1 path; '
                '(3) accepts two integers and an optional length parameter defaulting to 20 and returns the fibinacci '
                'sequence (of the optional parameter length) starting with the two integers.')
            code = agent.Coder.write_code(desc)
            stm = agent.Coder.create_stm(code)
            agent.memorize(stm)

            stm.name  # 'NumberSequences'
            agent.api(stm.name)  # ['is_prime', 'collatz', 'fibonacci']

            agent.NumberSequences.is_prime(101)  # True
            agent.NumberSequences.collatz(17)  # [17, 52, 26, 13, 40, 20, 10, 5, 16, 8, 4, 2, 1]
            agent.NumberSequences.fibonacci(2, 3, length=10)  # [2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

        """
        code = str(code)
        actions_conversation = None
        if actions is None:
            actions_conversation = OpenAIChat(
                system_prompt=self.determine_actions_prompt,
                model=self.model,
                stream=False,
                temperature=0.1)
            actions = actions_conversation.message(code + '\n\nUser: Return the API for the previous conversation:\n\n')
            actions = eval(actions)
            if not isinstance(actions, List):
                raise RuntimeError(f'Generated actions were not a list, but a list was needed.')
        if name is None:
            if actions_conversation is None:
                actions_conversation = code + f'\n\nThe selected actions are {actions}.'
            conversation = OpenAIChat(
                system_prompt=self.determine_name_prompt,
                model=self.model,
                stream=False,
                temperature=0.1)
            name = conversation.message(
                str(actions_conversation) + '\n\nUser: Write the API class name for the previous conversation:\n\n')

        return ShortTermModule(name=name, code=clean_code(code), actions=actions)

    def __call__(self, description: str, max_tries: Optional[int] = None, return_intermediate_tries: bool = False) -> str:
        return self.write_code(
            description=description, max_tries=max_tries, return_intermediate_tries=return_intermediate_tries)


Coder.register_action('write_code')
Coder.register_action('create_stm')
Coder.register_action('__call__')
Coder.register_task('Coder')
