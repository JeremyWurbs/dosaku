import copy
from typing import Dict, List, Generator, Optional, Union

import openai

from dosaku import Config, Service
from dosaku.utils import ifnone


class OpenAIChat(Service):
    name = 'OpenAIChat'
    config = Config()

    def __init__(
            self,
            system_prompt: str = 'You are a helpful assistant.',
            model: Optional[str] = None,
            stream: bool = False):
        openai.api_key = self.config['API_KEYS']['OPENAI']
        self.system_prompt = system_prompt
        self.model = ifnone(model, default=self.config['OPENAI']['DEFAULT_MODEL'])
        self.stream = stream
        self.history = None
        self.clear_chat()

    def message(self, message: str, **kwargs) -> Union[str, Generator[str, None, None]]:
        if self.stream:  # return generator object that will stream response
            return self._message_generator(message, **kwargs)
        else:  # return str response directly
            return self._message_return(message, **kwargs)

    def _update_history(self, message: str, record_interaction: bool = True) -> List[Dict[str, str]]:
        if record_interaction:
            self.history.append({'role': 'user', 'content': message})
            history = self.history
        else:
            history = copy.deepcopy(self.history)
            history.append({'role': 'user', 'content': message})
        return history

    def _message_return(self, message: str, record_interaction: bool = True) -> str:
        history = self._update_history(message, record_interaction=record_interaction)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=history,
            temperature=1.0,
            stream=False
        )['choices'][0]['message']['content']

        if record_interaction:
            self.history.append({'role': 'assistant', 'content': response})

        return response

    def _message_generator(self, message: str, record_interaction: bool = True) -> Generator[str, None, None]:
        history = self._update_history(message, record_interaction=record_interaction)

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=history,
            temperature=1.0,
            stream=True
        )

        partial_message = ''
        if record_interaction:
            self.history.append({'role': 'assistant', 'content': partial_message})
        for chunk in response:
            if len(chunk['choices'][0]['delta']) != 0:
                partial_message = partial_message + chunk['choices'][0]['delta']['content']
                if record_interaction:
                    self.history[-1]['content'] = partial_message
                yield partial_message

    def clear_chat(self):
        self.history = [{'role': 'system', 'content': self.system_prompt}]

    def __call__(self, message: str, **kwargs):
        return self.message(message, **kwargs)

    def __str__(self):
        conv_str = ''
        for message in self.history:
            conv_str += f'{message["role"]}: {message["content"]}\n\n'
        return conv_str


OpenAIChat.register_action('message')
OpenAIChat.register_action('clear_chat')
OpenAIChat.register_action('__call__')
OpenAIChat.register_task('OpenAIChat')
OpenAIChat.register_task('Chat')
