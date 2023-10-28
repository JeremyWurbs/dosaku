from typing import Optional

from dosaku import Agent
from dosaku.logic import Context, LogicNode
from dosaku.tasks import Chat


class Dosaku(Agent):
    name = 'Dosaku'

    def __init__(self, stream_chat: bool = True, **kwargs):
        super().__init__(**kwargs)

        self._assert_services_enabled()
        self._assert_executors_enabled()

        system_prompt = (
            'You are an AI personal assistant, named Dosaku.\n'
            '\n'
            'Be kind but direct. Do not use extra fluff language or say phrases like "thank you". If the user asks for '
            'code or the answer to a question, do not provide extra commentary, but just provide the answer with no '
            'extra language.\n'
            '\n'
            'For example, if the user asks to create a program that prints the numbers one to ten, say:\n'
            '\n'
            '```python\n'
            'from i in range(10):\n'
            '   print(i)\n'
            '```\n'
            '\n'
            'If you write code, always begin it with ```python and end it with ```.\n'
            '\n'
            'Finally, always stay in character as the best, most capable AI assistant— Dosaku.'
        )

        if self.config['REQUIRED_DOSAKU_MODULES']['Chat'] == 'OpenAIChat':
            self.learn(
                'Chat',
                module='OpenAIChat',
                stream=stream_chat,
                model=self.config['OPENAI']['DEFAULT_MODEL'],
                system_prompt=system_prompt,
                temperature=0.1,
            )
        else:
            self.learn('Chat', module=self.config['REQUIRED_DOSAKU_MODULES']['Chat'], stream=stream_chat)

        self.learn('OpenAIChat', module='OpenAIChat')
        self.learn('SpeechToText', module=self.config['REQUIRED_DOSAKU_MODULES']['SpeechToText'])
        self.learn('RealtimeSpeechToText', module=self.config['REQUIRED_DOSAKU_MODULES']['RealtimeSpeechToText'])
        self.learn('Spellchecker', module=self.config['REQUIRED_DOSAKU_MODULES']['Spellchecker'])
        self.learn('LogicEvaluator', module=self.config['REQUIRED_DOSAKU_MODULES']['LogicEvaluator'])
        self.learn('Coder', module=self.config['REQUIRED_DOSAKU_MODULES']['Coder'])

        for task in self.config['EXTRA_DOSAKU_MODULES']:
            if task not in self.tasks:
                self.learn(task, module=self.config['EXTRA_DOSAKU_MODULES'][task])

        self.context = Context(conversation=self.OpenAIChat)
        self.logic_root = self.create_logic()

    def logic(self, context: Optional[Context] = None) -> Context:
        if context is None:
            context = self.context
        next_node = self.logic_root
        while next_node is not None:
            context, next_node = next_node(context)
        return context

    def create_logic(self):
        root = LogicNode(
            label='root',
            evaluator=self.LogicEvaluator
        )

        gen_chat = LogicNode(
            label='general chat',
            action=self.OpenAIChat.act_on_context
        )

        request_for_code = LogicNode(
            label='request to write code',
            action=self.Coder.code_from_context
        )

        create_stm = LogicNode(
            label='request to create short term module (STM)',
            action=self.Coder.stm_from_context,
            evaluator=lambda context, labels: 'request to memorize short term module (STM)'
        )

        memorize_stm = LogicNode(
            label='request to memorize short term module (STM)',
            action=self.memorize_from_context
        )

        root.add_child(gen_chat)
        root.add_child(request_for_code)
        root.add_child(create_stm)
        create_stm.add_child(memorize_stm)

        return root

    def __call__(self, message: str):
        self.context.conversation.add_message(Chat.Message(sender='user', message=message))
        return self.logic()

