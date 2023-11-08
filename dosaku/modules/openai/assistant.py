from typing import Dict, List, Optional

from openai import OpenAI

from dosaku import Config, Module
from dosaku.tasks import Chat
from dosaku.utils import ifnone


class OpenAIAssistant(Module):
    name = 'OpenAIAssistant'
    config = Config()
    default_instructions = 'You are a helpful personal assistant. Answer user questions. Write code as necessary.'
    default_tools = [{'type': 'code_interpreter'}]
    default_model = 'gpt-4-1106-preview'

    def __init__(
        self,
        name: Optional[str] = None,
        instructions: Optional[str] = None,
        tools: Optional[List[Dict[str, str]]] = None,
        model: Optional[str] = None
    ):
        self.client = OpenAI(api_key=self.config['API_KEYS']['OPENAI'])

        self._assistant_name = ifnone(name, default=self.name)
        self.instructions = ifnone(instructions, default=self.default_instructions)
        self.tools = ifnone(tools, default=self.default_tools)
        self.model = ifnone(model, default=self.default_model)

        self.assistant = None
        self.thread = None
        self._history = None
        self.reset_chat()

    def reset_chat(self):
        self.assistant = self.client.beta.assistants.create(
            name=self._assistant_name,
            instructions=self.instructions,
            tools=self.tools,
            model=self.model)
        self.thread = self.client.beta.threads.create()
        self._history = list()

    def add_message(self, text: str):
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role='user',
            content=text
        )

    def message(self, text: str, instructions: Optional[str] = None) -> str:
        self.add_message(text)

        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions=instructions
        )
        while run.status not in ['completed', 'failed', 'expired', 'cancelled']:
            if run.status == 'requires_action':
                # TODO
                raise NotImplementedError
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
        if run.status != 'completed':
            raise RuntimeError(f'Message failed with status: {run.status}')

        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )

        conversation = list()
        for message in messages:
            conversation.append(self.parse_message(message_id=message.id))
        conversation.reverse()
        self._history = conversation

        return conversation[-1].message

    def parse_message(self, message_id) -> Chat.Message:
        # Retrieve the message object
        message = self.client.beta.threads.messages.retrieve(
            thread_id=self.thread.id,
            message_id=message_id)

        # Extract the message content
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []

        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

            # Gather citations based on annotation attributes
            if (file_citation := getattr(annotation, 'file_citation', None)):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')

            elif (file_path := getattr(annotation, 'file_path', None)):
                cited_file = self.client.files.retrieve(file_path.file_id)
                citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
                # Note: File download functionality not implemented above for brevity

        # Add footnotes to the end of the message before displaying to user
        message_content.value += '\n' + '\n'.join(citations)

        return Chat.Message(sender=message.role, message=message_content.value)

    def history(self) -> List[Chat.Message]:
        return self._history

    def __call__(self, message: str, **kwargs):
        return self.message(message, **kwargs)

    def __str__(self):
        conv_str = ''
        for message in self._history:
            conv_str += f'{message["role"]}: {message["content"]}\n\n'
        return conv_str


OpenAIAssistant.register_action('message')
OpenAIAssistant.register_action('history')
OpenAIAssistant.register_action('__call__')
OpenAIAssistant.register_action('__str__')
OpenAIAssistant.register_task('OpenAIAssistant')

OpenAIAssistant.register_task('Chat')
