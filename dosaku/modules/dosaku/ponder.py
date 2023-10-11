import os

import openai

from dosaku import Config, Service
from dosaku.modules.openai.conversation import OpenAIConversation


class Ponder(Service):
    """Ponder into existence."""

    name = 'Ponder'
    config = Config()

    def __init__(self, model='gpt-3.5-turbo'):
        openai.api_key = self.config['API_KEYS']['OPENAI']
        self.model = model

    def write_task(
            self,
            task_reqs: str,
            write_to_file: bool = False,
            filename: str = None,
            **_):
        system_prompt = """
        You are a Python developer, tasked with developing code that fits into a pre-existing python package called 
        Dosaku. When you respond you should respond only with the correct code response and nothing else. Do not include 
        ```python or any other accompanying text.
        
        There are two types of classes you have to write, Task and Module.
        
        Task classes must derive from the Task base class, which is accessible via the dosaku namespace. Task classes
        may then define any number of abstract methods which are required to describe the desired task. Finally, task
        classes must register themselves by calling the register_task() method without any arguments. Note that modules
        DO NOT import task classes directly, and thus cannot, in general, use any helper classes or enums defined by the
        task. As such, do not add helper classes or enums to the task class.
        
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
                raise NotImplementedError

        Chat.register_task()

        """

        conversation = OpenAIConversation(system_prompt=system_prompt, model=self.model)
        response = conversation.message(f'Write a Task class with the following requirements: {task_reqs}')

        if write_to_file:
            if filename is None:
                filename = conversation.message('What is the name of the file you would put the above code into? Just '
                                                'give me the raw filename with no explanation.')
            filename = os.path.join(self.config['DOSAKU']['PONDERED_TASK_DIR'], filename)
            print(f'Writing to file {filename}')
            with open(filename, 'w') as file:
                file.write(response)

        return response

    def write_module(self):
        pass

    def write_module_from_task(
            self,
            task_filename: str,
            module_reqs: str = None,
            write_to_file: bool = False,
            filename: str = None,
            write_sample: bool = True,
            **_
    ) -> OpenAIConversation:
        system_prompt = """
        You are a Python developer, tasked with developing code that fits into a pre-existing python package called 
        Dosaku. When you respond you should respond only with the correct code response and nothing else. Do not include 
        ```python or any other accompanying text.
        
        There are two types of classes you have to write, Task and Module.
        
        Task classes define a set of abstract methods which must be implemented by Module classes. Module classes must
        derive from the Module base class, which is accessible via the dosaku namespace. Module classes must implement
        all abstract methods from the associated Task class. Module classes may implement and use any additional methods
        as necessary. Finally, module classes must register the task they complete by call the class method 
        register_task(task_name), filling in the name of the appropriate task.
        
        For example, the following is a task class for a conversational bot:
        
        
        
        from abc import abstractmethod
        
        from dosaku import Task


        class Chat(Task):
            name = 'Chat'

            def __init__(self):
                super().__init__()

            @abstractmethod
            def chat(self, message: str, **kwargs):
                raise NotImplementedError


        Chat.register_task()

        
        
        One possible module which would implement this task is as follows:
        
        
        
        from dosaku import Module
        
        
        class EchoBot(Module):
            name = 'EchoBot'
        
            def __init__(self):
                super().__init__()
        
            def chat(self, message: str) -> str:
                return f'Hi, I\'m EchoBot. You said, \"{message}\".'
        
        
        EchoBot.register_task(task='Chat')
        
        """
        conversation = OpenAIConversation(system_prompt=system_prompt, model=self.model)

        task_path = os.path.join(self.config['DOSAKU']['PONDERED_TASK_DIR'], task_filename)
        task_file = open(task_path, 'r')
        task_str = task_file.read()

        message = f'Write a Module class for the following Task class:\n\n\n{task_str}\n\n\n'
        if module_reqs is not None:
            message += f'The Module class has the following additional requirements: {module_reqs}'

        response = conversation.message(message)

        if write_to_file:
            if filename is None:
                filename = conversation.message('What is the name of the file you would put the above code into? Just '
                                                'give me the raw filename with no explanation.')
            full_path = os.path.join(self.config['DOSAKU']['PONDERED_MODULE_DIR'], filename)
            print(f'Writing module to file {full_path}')
            with open(full_path, 'w') as file:
                file.write(response)

        if write_sample:
            message = """
            Write a sample for the module you just wrote. The sample can be a python gradio app or standalone 
            executable. If you create a gradio app, use a gr.Blocks app with a chatbot, as demonstrated below. In either 
            case, the sample must clearly demonstrate to an end user how to use the module you wrote from end to 
            end. The sample must also make use of the dosaku Agent class. The agent class has a learn method which can
            be used to learn a task as well as setting which module to use for the task. The task name then becomes a 
            property of the agent, with each abstract method the task had defined further becoming a property of the 
            task.
            
            For example, here is how to define a dosaku Agent to use the chat task and module from before:
            
            
            
            from dosaku import Agent
            
            agent = Agent()
            agent.learn('Chat', module='EchoBot')
            response = agent.Chat.chat('Hello!')
            print(response)  # Hi, I'm EchoBot. You said: "Hello!".
            
            
            
            And here is an end to end gradio app example, again using the Chat task and module from before:
            
            
            
            import gradio as gr
            
            from dosaku import Agent
            
            
            agent = Agent()
            agent.learn('Chat', module='EchoBot')
            
            with gr.Blocks() as sample:
                chatbot = gr.Chatbot()
                msg = gr.Textbox()
                clear = gr.ClearButton([msg, chatbot])
            
                def respond(message, chat_history):
                    bot_message = agent.Chat.chat(message)
                    chat_history.append((message, bot_message))
                    return '', chat_history
            
                msg.submit(respond, [msg, chatbot], [msg, chatbot])
            
            
            if __name__ == "__main__":
                sample.launch()

            
            """
            sample = conversation.message(message)
            if write_to_file:
                full_path = os.path.join(self.config['DOSAKU']['PONDERED_SAMPLE_DIR'], filename)
                print(f'Writing sample to file {full_path}')
                with open(full_path, 'w') as file:
                    file.write(sample)

        return conversation


Ponder.register_task('WriteTask')
Ponder.register_task('WriteModule')
Ponder.register_task('WriteModuleFromTask')
