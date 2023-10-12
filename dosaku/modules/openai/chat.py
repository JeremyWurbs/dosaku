import copy

import openai

from dosaku import Config, Service


class OpenAIChat(Service):
    name = 'OpenAIChat'
    config = Config()

    def __init__(self, system_prompt: str = 'You are a helpful assistant.', model='gpt-3.5-turbo'):
        self.system_prompt = system_prompt
        self.model = model
        self.history = None
        self.clear_chat()

    def message(self, message: str, stream: bool = False, record_interaction: bool = True):
        if record_interaction:
            self.history.append({'role': 'user', 'content': message})
            history = self.history
        else:
            history = copy.deepcopy(self.history)
            history.append({'role': 'user', 'content': message})

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=history,
            temperature=1.0,
            stream=stream
        )['choices'][0]['message']['content']

        if record_interaction:
            self.history.append({'role': 'assistant', 'content': response})

        return response

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
