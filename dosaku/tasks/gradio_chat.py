from abc import abstractmethod
import time
from typing import List

from dosaku.tasks import Chat


class GradioChat(Chat):
    """Interface for a gradio.ChatInterface compatible chatbot."""
    name = 'GradioChat'

    def __init__(self):
        super().__init__()

    @abstractmethod
    def predict(self, message: str, history: List[List[str]], **kwargs):
        """Generate a response given a message and chat history.

        Refer to the associated [Gradio documentation](https://www.gradio.app/docs/chatinterface) for further details.

        Args:
            message: The (human) message.
            history: The conversation up until that point, as a list of [message, response].

        Returns:
            A response string.

        Example::

            from dosaku import Agent

            agent = Agent()
            agent.learn('GradioChat', module='EchoBot')
            history = list()

            message = "Hello!"
            response = agent.Chat.predict(message, history)  # "Hello Hello!! I'm EchoBot."
            history.append([message, response])

            message = "I'm not Hello, I was just.."
            response = agent.Chat.predict(message, history)  # "Hello I'm not Hello, I was just..! I'm EchoBot."

        """
        raise NotImplementedError

    def predict_generator(self, message: str, history: List[List[str]], **kwargs):
        response = self.predict(message=message, history=history, **kwargs)
        for i in range(len(response)):
            time.sleep(0.05)
            yield response[: i + 1]


GradioChat.register_task()
