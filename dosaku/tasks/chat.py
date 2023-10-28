from abc import abstractmethod
from dataclasses import dataclass
from typing import Generator, List, Union

from dosaku import Task


class Chat(Task):
    """Interface for a generic conversational chatbot.

    A chat module is not obligated to support streaming, but if stream=True is passed in on init and the module does not
    support streaming, it must raise an OptionNotSupported exception.

    Args:
        stream: Whether to stream messages.
    """

    @dataclass
    class Message:
        sender: str
        message: str

    name = 'Chat'

    @abstractmethod
    def __init__(self, stream: bool = False, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def message(self, message: str, **kwargs) -> Union[str, Generator[str, None, None]]:
        """Send a message to the agent and get a response.

        It is up to the chat module whether a chat history is kept and used.

        Args:
            message: The message to send the chat agent.

        Returns:
            An AI chat response. The response may be in one of two forms:

                - non-streaming: The expected default behavior, if a module is in non-streaming mode it should return
                    the response as a string directly;
                - streaming: If the module is set to stream the response, it should return a generator object that
                    yields an updated string response every iteration;

        Non-streaming Example::

            from dosaku import Agent

            agent = Agent()
            agent.learn('Chat', module='EchoBot', stream=False)
            response = agent.Chat.message('Hello!')  # Hi, I'm EchoBot. You said: "Hello!".

        Streaming Example::

            from dosaku import Agent

            agent = Agent()
            agent.learn('Chat', module='EchoBot', stream=True)
            for partial_response in agent.Chat.message('Hello!):
                print(partial_response)

            # H
            # Hi
            # Hi,
            # ...
            # Hi, I'm EchoBot. You said: "Hello
            # Hi, I'm EchoBot. You said: "Hello!
            # Hi, I'm EchoBot. You said: "Hello!"

        OpenAI GPT Streaming in a Gradio App Example (Requires the OpenAI service)::

            import gradio as gr
            from dosaku import Agent, Config

            agent = Agent(enable_services=True)
            agent.learn('Chat', module='OpenAIChat', model=Config()['OPENAI']['DEFAULT_MODEL'], stream=True)

            def predict(message, _):
                for partial_response in agent.Chat(message):  # __call__() defaults to message()
                    yield partial_response

            gr.ChatInterface(predict).queue().launch()

        """

    @abstractmethod
    def add_message(self, message: Message):
        """Add message to the conversation history without generating response."""
        raise NotImplementedError

    @abstractmethod
    def reset_chat(self):
        """Reset the chat to its starting state."""
        raise NotImplementedError

    @abstractmethod
    def history(self) -> List[Message]:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, *args, **kwargs):
        return self.message(*args, **kwargs)

    @abstractmethod
    def __str__(self):
        raise NotImplementedError


Chat.register_task()
