import os

import openai

from dosaku import Config, Service
from dosaku.modules.openai.conversation import OpenAIConversation


class Ponder(Service):
    """Ponder into existence."""

    name = 'Ponder'
    config = Config()

    def __init__(self):
        openai.api_key = self.config['API_KEYS']['OPENAI']

    def write_task(self, task_reqs: str, write_to_file: bool = False, filename: str = None, **kwargs):
        system_prompt = """
        You are a Python developer, tasked with developing code that fit into a pre-existing python package call Dosaku.
        When you response you should respond only with the correct code response and nothing else. Do not include 
        ```python or any other accompanying text.
        
        There are two types of classes you have to write, Task and Module.
        
        Task classes must derive from the Task base class, which is accessible via the dosaku namespace. Task classes
        may then define any number of abstract methods which are required to describe the desired task. Finally, task
        classes must register themselves by calling the register_task() method without any arguments.
        
        For example, the following is a task class for a conversational bot:
        
        from abc import abstractmethod

        from dosaku import Task

        class Chat(Task):
            \"\"\"Interface for a generic conversational chatbot.\"\"\"
            name = 'Chat'

            def __init__(self):
                super().__init__()

            @abstractmethod
            def chat(self, message: str, **kwargs):
                \"\"\"Send a message to the agent and get a response.

                It is up to the chat module whether a chat history is kept and used.

                Args:
                    message: The message to send the chat agent.

                Returns:
                    A response.

                Example::

                    from dosaku import Agent

                    agent = Agent()
                    agent.learn('Chat', module='EchoBot')
                    response = agent.Chat.chat('Hello!')  #
                \"\"\"

        Chat.register_task()

        """

        conversation = OpenAIConversation(system_prompt=system_prompt)
        response = conversation.message(f'Write a Task class with the following requirements: {task_reqs}')

        if write_to_file:
            if filename is None:
                filename = conversation.message('What is the name of the file you would put the above code into? Just '
                                                'give me the raw filename with no explanation.')
            filename = os.path.join(self.config['DOSAKU']['TASK_DIR'], filename)
            print(f'Writing to file {filename}')
            with open(filename, 'w') as file:
                file.write(response)

        return response

    def write_module(self, context: str, module_reqs: str, examples: str, **kwargs):
        pass


Ponder.register_task('WriteTask')
Ponder.register_task('WriteModule')
