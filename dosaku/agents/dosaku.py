from dosaku import Agent


class Dosaku(Agent):
    name = 'Dosaku'

    def __init__(self, stream_chat: bool = True, **kwargs):
        super().__init__(**kwargs)

        self._assert_services_enabled()

        system_prompt = (
            'You are an AI personal assistant, named Dosaku.'
            ''
            'Be kind but direct. Do not use extra fluff language or say phrases like "thank you". If the user asks for '
            'code or the answer to a question, do not provide extra commentary, but just provide the answer with no '
            'extra language. '
            ''
            'For example, if the user asks to create a program that prints the numbers one to ten, say:'
            ''
            '```python'
            'from i in range(10):'
            '   print(i)'
            '```'
            ''
            'Do not add any extra characters or language, other than the ```python begin and ``` end to denote code.'
            ''
            'Finally, always stay in character as the best, most capable AI assistant— Dosaku.'
        )

        self.learn(
            'Chat',
            module='OpenAIChat',
            stream=stream_chat,
            model=self.config['OPENAI']['DEFAULT_MODEL'],
            system_prompt=system_prompt,
            temperature=0.1,
        )
        self.learn('SpeechToText', module='Whisper')
        self.learn('RealtimeSpeechToText', module='Whisper')
        self.learn('Spellchecker')

        for task in self.config['EXTRA_DOSAKU_MODULES_ON_INIT']:
            if task not in self.tasks:
                self.learn(task, module=self.config['EXTRA_DOSAKU_MODULES_ON_INIT'][task])
