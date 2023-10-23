from typing import List, Optional, Union

from dosaku import Config, Executor, Service
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
        'be able to run directly in a python interpreter. That is, DO NOT add any explanatory text or markdown code, '
        'such as ```python. Any explanatory code MUST be written as python comments.'
        ''
        'After you write code it will be run. If there are errors you will be given the errors. You should respond by '
        'rewriting ALL of the code with the errors corrected.'
    )

    def __init__(self, model: str = None):
        super().__init__()
        self.model = ifnone(model, default=self.config['OPENAI']['DEFAULT_MODEL'])

    def write(
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
            code = agent.Coder('Write a method that takes two integers and returns their
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

    def __call__(self, description: str, max_tries: Optional[int] = None, return_intermediate_tries: bool = False) -> str:
        return self.write(description=description, max_tries=max_tries, return_intermediate_tries=return_intermediate_tries)


Coder.register_action('write')
Coder.register_action('__call__')
Coder.register_task('Coder')
