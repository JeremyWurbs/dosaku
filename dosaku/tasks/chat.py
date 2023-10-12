from abc import abstractmethod

from dosaku import Task


class Chat(Task):
    """Interface for a generic conversational chatbot."""
    name = 'Chat'

    def __init__(self):
        super().__init__()

    @abstractmethod
    def message(self, message: str, **kwargs):
        """Send a message to the agent and get a response.

        It is up to the chat module whether a chat history is kept and used.

        Args:
            message: The message to send the chat agent.

        Returns:
            A response.

        Example::

            from dosaku import Agent

            agent = Agent()
            agent.learn('Chat', module='EchoBot')
            response = agent.Chat.message('Hello!')  #
        """

    @abstractmethod
    def __call__(self, *args, **kwargs):
        return self.message(*args, **kwargs)


Chat.register_task()
