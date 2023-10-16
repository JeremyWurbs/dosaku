from dosaku import Agent


class Dosaku(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.services_enabled is False:
            raise ValueError('Dosaku requires services to be enabled. Pass in enable_services=True on init.')

        system_prompt = (
            'You are an AI personal assistant, named Dosaku.'
            ''
            'Be kind but direct. Do not use extra fluff language or say phrases like "thank you". If the user asks for '
            'code or the answer to a question, do not provide extra commentary, but just provide the answer with no '
            'extra language. '
            ''
            'For example, if the user asks to create a program that prints the numbers one to ten, say:'
            ''
            'from i in range(10):'
            '   print(i)'
            ''
            'Do not add any extra characters or language, such as ```python'
            ''
            'Finally, always stay in character as the best, most capable AI assistant— Dosaku.'
        )
        self.learn(
            'Chat',
            module='OpenAIChat',
            stream=True,
            model=self.config['OPENAI']['DEFAULT_MODEL'],
            system_prompt=system_prompt
        )

        if self.services_enabled:
            services_key = 'DOSAKU_SERVICES_LOAD_ON_INIT'
            for task in self.config[services_key]:
                if task not in self.tasks:
                    self.learn(task, module=self.config[services_key][task])

        modules_key = 'DOSAKU_MODULES_LOAD_ON_INIT'
        for task in self.config[modules_key]:
            if task not in self.tasks:
                self.learn(task, module=self.config[modules_key][task])

