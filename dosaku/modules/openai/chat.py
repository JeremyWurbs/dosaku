import copy
from typing import Dict, List, Generator, Optional, Union

import openai

from dosaku import Config, Service
from dosaku.logic import Context
from dosaku.tasks import Chat
from dosaku.utils import ifnone


class OpenAIChat(Service):
    name = 'OpenAIChat'
    config = Config()

    def __init__(
            self,
            system_prompt: str = 'You are a helpful assistant.',
            model: Optional[str] = None,
            stream: bool = False,
            temperature: float = 1.):
        openai.api_key = self.config['API_KEYS']['OPENAI']
        self.system_prompt = system_prompt
        self.model = ifnone(model, default=self.config['OPENAI']['DEFAULT_MODEL'])
        self.stream = stream
        self.temperature = temperature
        self._history = None
        self.reset_chat()

    def message(self, message: str, **kwargs) -> Union[str, Generator[str, None, None]]:
        if self.stream:  # return generator object that will stream response
            return self._message_generator(message, **kwargs)
        else:  # return str response directly
            return self._message_return(message, **kwargs)

    def add_message(self, message: Chat.Message):
        self._history.append({'role': message.sender, 'content': message.message})

    def _update_history(
            self,
            message: str,
            role: str = 'user',
            record_interaction: bool = True
    ) -> List[Dict[str, str]]:
        if record_interaction:
            self._history.append({'role': role, 'content': message})
            history = self._history
        else:
            history = copy.deepcopy(self._history)
            history.append({'role': role, 'content': message})
        return history

    def _message_return(
            self,
            message: str,
            role: str = 'user',
            record_interaction: bool = True
    ) -> str:
        history = self._update_history(message, role=role, record_interaction=record_interaction)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=history,
            temperature=self.temperature,
            stream=False,
        )['choices'][0]['message']['content']

        if record_interaction:
            self._history.append({'role': 'assistant', 'content': response})

        return response

    def _message_generator(
            self,
            message: str,
            role: str = 'user',
            record_interaction: bool = True
    ) -> Generator[str, None, None]:
        history = self._update_history(message, role=role, record_interaction=record_interaction)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=history,
            temperature=self.temperature,
            stream=True
        )

        partial_message = ''
        if record_interaction:
            self._history.append({'role': 'assistant', 'content': partial_message})
        for chunk in response:
            if len(chunk['choices'][0]['delta']) != 0:
                partial_message = partial_message + chunk['choices'][0]['delta']['content']
                if record_interaction:
                    self._history[-1]['content'] = partial_message
                yield partial_message

    def reset_chat(self, system_prompt: Optional[str] = None):
        if system_prompt is not None:
            self.system_prompt = system_prompt
        self._history = [{'role': 'system', 'content': self.system_prompt}]

    def history(self) -> List[Chat.Message]:
        messages = list()
        for message in self._history:
            messages.append(Chat.Message(sender=message['role'], message=message['content']))
        return messages

    def act_on_context(self, context: Context) -> Context:
        """Generate a chat response based on the given context.

        Note that the context.conversation attribute must be set to this module instance.
        """
        role = self._history[-1]['role']
        content = self._history[-1]['content']
        self._history = self._history[:-1]  # remove last message
        self.message(message=content, role=role)  # resend message to generate response
        return context

    def __call__(self, message: str, **kwargs):
        return self.message(message, **kwargs)

    def __str__(self):
        conv_str = ''
        for message in self._history:
            conv_str += f'{message["role"]}: {message["content"]}\n\n'
        return conv_str


OpenAIChat.register_action('message')
OpenAIChat.register_action('add_message')
OpenAIChat.register_action('reset_chat')
OpenAIChat.register_action('history')
OpenAIChat.register_action('act_on_context')
OpenAIChat.register_action('__call__')
OpenAIChat.register_action('__str__')
OpenAIChat.register_task('OpenAIChat')

OpenAIChat.register_task('Chat')
OpenAIChat.register_action('LogicActor')
