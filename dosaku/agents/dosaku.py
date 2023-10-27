from dosaku import Agent


class Dosaku(Agent):
    name = 'Dosaku'

    def __init__(self, stream_chat: bool = True, **kwargs):
        super().__init__(**kwargs)

        self._assert_services_enabled()

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

        self.learn('SpeechToText', module=self.config['REQUIRED_DOSAKU_MODULES']['SpeechToText'])
        self.learn('RealtimeSpeechToText', module=self.config['REQUIRED_DOSAKU_MODULES']['RealtimeSpeechToText'])
        self.learn('Spellchecker', module=self.config['REQUIRED_DOSAKU_MODULES']['Spellchecker'])
        self.learn('TextEvaluator', module=self.config['REQUIRED_DOSAKU_MODULES']['TextEvaluator'])

        for task in self.config['EXTRA_DOSAKU_MODULES']:
            if task not in self.tasks:
                self.learn(task, module=self.config['EXTRA_DOSAKU_MODULES'][task])
