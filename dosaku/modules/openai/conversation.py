import openai

from dosaku import Config, Service


class OpenAIConversation(Service):
    name = 'OpenAIConversation'
    config = Config()

    def __init__(self, system_prompt: str = 'You are a helpful assistant.'):
        self.history = [{'role': 'system', 'content': system_prompt}]

    def message(self, message, stream=False):
        self.history.append({'role': 'user', 'content': message})

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=self.history,
            temperature=1.0,
            stream=stream
        )['choices'][0]['message']['content']
        self.history.append({'role': 'assistant', 'content': response})

        return response

    def __call__(self, *args, **kwargs):
        self.message(**kwargs)


OpenAIConversation.register_action('message')
OpenAIConversation.register_action('__call__')
OpenAIConversation.register_task('OpenAIConversation')
