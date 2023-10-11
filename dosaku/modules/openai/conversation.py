import openai

from dosaku import Config, Service


class OpenAIConversation(Service):
    name = 'OpenAIConversation'
    config = Config()

    def __init__(self, system_prompt: str = 'You are a helpful assistant.', model='gpt-3.5-turbo'):
        self.system_prompt = system_prompt
        self.model = model
        self.history = None
        self.clear_chat()

    def message(self, message: str, stream: bool = False):
        self.history.append({'role': 'user', 'content': message})

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=self.history,
            temperature=1.0,
            stream=stream
        )['choices'][0]['message']['content']
        self.history.append({'role': 'assistant', 'content': response})

        return response

    def clear_chat(self):
        self.history = [{'role': 'system', 'content': self.system_prompt}]

    def __call__(self, message: str):
        return self.message(message)

    def __str__(self):
        conv_str = ''
        for message in self.history:
            conv_str += f'{message["role"]}: {message["content"]}\n\n'
        return conv_str


OpenAIConversation.register_action('message')
OpenAIConversation.register_action('clear_chat')
OpenAIConversation.register_action('__call__')
OpenAIConversation.register_task('OpenAIConversation')