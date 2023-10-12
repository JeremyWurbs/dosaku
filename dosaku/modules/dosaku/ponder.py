import os
from typing import Optional

import openai

from dosaku import Config, Service
from dosaku.modules.openai.chat import OpenAIChat
from dosaku.utils import ifnone


class Ponder(Service):
    """Ponder into existence."""

    name = 'Ponder'
    config = Config()
    default_system_prompt = (
        'You are a Python developer, tasked with developing code that fits into a pre-existing python package called '
        'Dosaku. When you respond you should respond only with the correct code response and nothing else. Do not '
        'include ```python or any other accompanying text.\n'
        '\n'
        'There are two types of classes you have to write, Task and Module classes, in addition to unit tests, '
        'samples and apps you will have to write as well.\n'
        '\n'
        'Task classes derive from the Task base class, which is accessible via the dosaku namespace. Task classes may '
        'then define any number of abstract methods which are required for the task. Finally, task classes must '
        'register themselves by calling the register_task() method without any arguments. Note that in the end, the '
        'user will only have access to methods defined by the Task (and NOT any extra methods defined by the Module), '
        'so it is important to include all desired methods in the task itself. Note also that Module classes DO NOT '
        'import task classes directly, and so cannot use any helper classes or enums defined by the task. As such, DO'
        'include all requisite abstract methods necessary for the task, DO NOT include any helper classes or enums, '
        'even if they are needed by the module.\n'
        '\n'
        '\n'
        'For example, the following is a task class for a conversational chatbot:\n'
        '\n'
        '\n'
        '\n'
        'from abc import abstractmethod\n'
        '\n'
        'from dosaku import Task\n'
        '\n'
        'class Chat(Task):\n'
        '   \"\"\"Interface for a generic conversational chatbot.\"\"\"\n'
        '   name = \'Chat\'\n'
        '\n'
        '   def __init__(self):\n'
        '       super().__init__()\n'
        '\n'
        '   @abstractmethod\n'
        '   def chat(self, message: str, **kwargs) -> str:\n'
        '       \"\"\"Send a message to the agent and get a response.\n'
        '\n'
        '       It is up to the chat module whether a chat history is kept and used.\n'
        '\n'
        '       Args:\n'
        '           message: The message to send to the chat agent.\n'
        '\n'
        '       Returns:\n'
        '           A chat response.\n'
        '\n'
        '       Example::\n'
        '\n'
        '           from dosaku import Agent\n'
        '\n'
        '           agent = Agent()\n'
        '           agent.learn(\'Chat\')\n'
        '           response = agent.Chat.chat(\'Hello!\')\n'
        '       \"\"\"\n'
        '       raise NotImplementedError\n'
        '\n'
        '\n'
        '   Chat.register_task()\n'
        '\n'
        '\n'
        '\n'
        'Module classes must derive from the Module base class, which is accessible via the dosaku namespace. Module '
        'classes must implement all abstract methods from the associated task class. Module classes may implement and '
        'use any additional methods as necessary, but they will be private and end users will not be able to call them '
        'directly. Finally, module classes must register the task they complete by calling the class method'
        'register_task(task_name), filling in the name of the appropriate task.\n'
        '\n'
        'For example, one possible module implementation for the Chat task above is as follows:\n'
        '\n'
        '\n'
        '\n'
        'from dosaku import Module\n'
        '\n'
        '\n'
        'class EchoBot(Module):\n'
        '   name = \'EchoBot\'\n'
        '\n'
        '   def __init__(self):\n'
        '       super().__init__()\n'
        '\n'
        '   def chat(self, message: str) -> str:\n'
        '       return f\'Hi, I\'m EchoBot. You said, \"{message}\".\n'
        '\n'
        '\n'
        'EchoBot.register_task(task=\'Chat\')\n'
        '\n'
        '\n'
        '\n'
        '\n')
    task_fullpath = lambda filename: os.path.join(Ponder.config['DOSAKU']['PONDERED_TASK_DIR'], filename)
    module_fullpath = lambda filename: os.path.join(Ponder.config['DOSAKU']['PONDERED_MODULE_DIR'], filename)
    unit_test_fullpath = lambda filename: os.path.join(Ponder.config['DOSAKU']['PONDERED_UNIT_TEST_DIR'], filename)
    sample_fullpath = lambda filename: os.path.join(Ponder.config['DOSAKU']['PONDERED_SAMPLE_DIR'], filename)
    app_fullpath = lambda filename: os.path.join(Ponder.config['DOSAKU']['PONDERED_APP_DIR'], filename)

    def __init__(self, model='gpt-3.5-turbo'):
        openai.api_key = self.config['API_KEYS']['OPENAI']
        self.model = model

    def _get_filename(self, conversation: OpenAIChat) -> str:
        output_filename = conversation.message(
            'What is the name of the file you would put the above code into? Just give me the raw filename '
            'with no explanation.',
            record_interaction=False)
        return output_filename

    def _load_file(self, filename: str) -> str:
        with open(filename, 'r') as file:
            file_str = file.read()
        return file_str

    def _save_file(self, filename: str, contents: str):
        with open(filename, 'w') as file:
            file.write(contents)

    def write_task(
            self,
            task_reqs: str,
            write_to_file: bool = False,
            save_filename: str = None
    ) -> OpenAIChat:
        conversation = OpenAIChat(system_prompt=self.default_system_prompt, model=self.model)
        response = conversation.message(f'Write a Task class in line with the following instructions: {task_reqs}')

        if write_to_file:
            save_filename = ifnone(save_filename, default=self._get_filename(conversation))
            self._save_file(filename=Ponder.task_fullpath(save_filename), contents=response)

        return conversation

    def write_module(
            self,
            conversation: Optional[OpenAIChat] = None,
            task_filename: Optional[str] = None,
            module_reqs: Optional[str] = None,
            write_to_file: bool = False,
            save_filename: Optional[str] = None
    ) -> OpenAIChat:
        if task_filename is None and conversation is None:
            raise ValueError('At least one of task_filename or conversation must not be None, but both were.')

        if conversation is None:
            conversation = OpenAIChat(system_prompt=self.default_system_prompt, model=self.model)
            task_str = self._load_file(Ponder.task_fullpath(task_filename))
            message = f'Write a Module class for the following Task class:\n\n\n{task_str}\n\n\n'

        else:
            message = 'Write a Module class for the task class you just wrote.\n\n'

        if module_reqs is not None:
            message += f'The Module class has the following additional requirements: {module_reqs}'

        response = conversation.message(message)

        if write_to_file:
            save_filename = ifnone(save_filename, default=self._get_filename(conversation))
            self._save_file(filename=Ponder.module_fullpath(save_filename), contents=response)

        return conversation

    def write_unit_test(
            self,
            conversation: Optional[OpenAIChat] = None,
            task_filename: Optional[str] = None,
            module_filename: Optional[str] = None,
            write_to_file: bool = False,
            save_filename: str = None
    ) -> OpenAIChat:
        if conversation is None:
            conversation = OpenAIChat(system_prompt=self.default_system_prompt, model=self.model)
            message = 'Write a set of pytest unit tests for the following task and module class.\n\n'

            if task_filename is not None:
                task_str = self._load_file(Ponder.task_fullpath(task_filename))
                message += f'The task class is given as follows:\n\n\n{task_str}\n\n\n'

            module_str = self._load_file(Ponder.module_fullpath(module_filename))
            message += f'The module class is given as follows:\n\n\n{module_str}\n\n\n'

        else:
            message = 'Write a set of pytest unit tests for the task and module classes you just wrote.'

        response = conversation.message(message)

        if write_to_file:
            save_filename = ifnone(save_filename, default=self._get_filename(conversation))
            self._save_file(filename=Ponder.unit_test_fullpath(save_filename), contents=response)

        return conversation

    def write_sample(
            self,
            conversation: Optional[OpenAIChat] = None,
            task_filename: Optional[str] = None,
            module_filename: Optional[str] = None,
            write_to_file: bool = False,
            save_filename: Optional[str] = None
    ) -> OpenAIChat:
        if conversation is None and (task_filename is None or module_filename is None):
            raise ValueError('Either a conversation or both task_filename and module_filename must be given.')

        if conversation is None:
            message = (
                'Write a sample for the following task and module class.'
            )

            task_str = self._load_file(Ponder.task_fullpath(task_filename))
            message += f'The task class is given as follows:\n\n\n{task_str}\n\n\n'

            module_str = self._load_file(Ponder.module_fullpath(module_filename))
            message += f'The module class is given as follows:\n\n\n{module_str}\n\n\n'

        else:
            message = 'Write a sample for the module you just wrote. '

        message += (
            'The sample should be a standalone python executable. The sample must clearly demonstrate to an end user '
            'how to use the module you wrote from end to end. The sample must also make use  of the dosaku Agent '
            'class. The agent class has a learn method which can be used to learn a task as well as setting which '
            'module to use for the task. The task name then becomes a property of the agent, with each abstract method '
            'defined by the task further becoming a property of agent.TaskName.\n'
            '\n'
            'For example, here is how to define a dosaku Agent to use the chat task and module from before:\n'
            '\n'
            '\n'
            '\n'
            'from dosaku import Agent\n'
            '\n'
            'agent = Agent()\n'
            'agent.learn(\'Chat\', module=\'EchoBot\')\n'
            'response = agent.Chat.chat(\'Hello!\')\n'
            'print(response)  # Hi, I\'m EchoBot. You said: \"Hello!\".\n'
            '\n'
            '\n'
            '\n'
            'Note that the agent can only use the abstract methods defined by the task. Even if the module defined '
            'more methods to use internally, those methods are not available to the agent.\n'
            )

        sample = conversation.message(message)
        if write_to_file:
            save_filename = ifnone(save_filename, default=self._get_filename(conversation))
            self._save_file(filename=Ponder.sample_fullpath(save_filename), contents=sample)

        return conversation

    def write_app(
            self,
            conversation: Optional[OpenAIChat] = None,
            task_filename: Optional[str] = None,
            module_filename: Optional[str] = None,
            write_to_file: bool = False,
            save_filename: str = None
    ) -> OpenAIChat:

        if conversation is None and (task_filename is None or module_filename is None):
            raise ValueError('Either a conversation or both task_filename and module_filename must be given.')

        if conversation is None:
            message = (
                'Write an app for the following task and module class.'
            )

            task_str = self._load_file(Ponder.task_fullpath(task_filename))
            message += f'The task class is given as follows:\n\n\n{task_str}\n\n\n'

            module_str = self._load_file(Ponder.module_fullpath(module_filename))
            message += f'The module class is given as follows:\n\n\n{module_str}\n\n\n'

        else:
            message = 'Write an app for the module you just wrote. '

        message += (
            'The app should be an end to end gradio app.\n'
            '\n'
            'For example, the following gradio app is a sufficient end to end example, again using the Chat task and '
            'module from before:\n'
            '\n'
            '\n'
            '\n'
            'import gradio as gr\n'
            '\n'
            'from dosaku import Agent\n'
            '\n'
            '\n'
            'agent = Agent()\n'
            'agent.learn(\'Chat\', module\'EchoBot\')\n'
            '\n'
            'with gr.Blocks() as app:\n'
            '   chatbot = gr.Chatbot()\n'
            '   msg = gr.Textbox()\n'
            '   clear = gr.ClearButton([msg, chatbot])\n'
            '\n'
            '   def respond(message, chat_history):\n'
            '       bot_message = agent.Chat.chat(message)\n'
            '       chat_history.append((message, bot_message))\n'
            '       return '', chat_history\n'
            '\n'
            '   msg.submit(respond, [msg, chatbot], [msg, chatbot])\n'
            '\n'
            '\n'
            'if __name__ == "__main__":\n'
            '   app.launch()\n'
            '\n'
            '\n'
            '\n'
            'Notice how this app is created. We create a dosaku Agent, have it learn the task via the module we '
            'created, then we create a chatbot and use the agent to help built the respond() method using our module. '
            'You can use this same strategy to create your app, just change the respond() method to return a response '
            'generated by the module you created. Remember that the agent and app can only use the abstract methods '
            'defined by the task, and cannot use or have any access to any extra methods defined by the module. If you '
            'need to recreate some functions of the module within the app, that is okay.\n'
        )

        app = conversation.message(message)
        if write_to_file:
            save_filename = ifnone(save_filename, default=self._get_filename(conversation))
            self._save_file(filename=Ponder.app_fullpath(save_filename), contents=app)

        return conversation

    def ponder(
            self,
            reqs: str,
            save_filename: str,
            write_to_file: bool = False,
    ) -> OpenAIChat:
        convo = self.write_task(task_reqs=reqs, write_to_file=write_to_file, save_filename=save_filename)
        convo = self.write_module(conversation=convo, write_to_file=write_to_file, save_filename=save_filename)
        convo = self.write_sample(conversation=convo, write_to_file=write_to_file, save_filename=save_filename)
        convo = self.write_app(conversation=convo, write_to_file=write_to_file, save_filename=save_filename)
        convo = self.write_unit_test(conversation=convo,write_to_file=write_to_file, save_filename=save_filename)

        return convo

    def __call__(self, *args, **kwargs):
        return self.ponder(*args, **kwargs)


Ponder.register_action(Ponder.write_task)
Ponder.register_action(Ponder.write_module)
Ponder.register_action(Ponder.write_sample)
Ponder.register_action(Ponder.write_app)
Ponder.register_action(Ponder.write_unit_test)
Ponder.register_action(Ponder.ponder)
Ponder.register_action(Ponder.__call__)
Ponder.register_task('Ponder')
Ponder.register_task('WriteTask')
Ponder.register_task('WriteModule')
Ponder.register_task('WriteModuleFromTask')
