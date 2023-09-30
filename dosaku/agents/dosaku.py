from dosaku import Agent


class Dosaku(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        modules_key = 'DOSAKU_MODULES_LOAD_ON_INIT'
        for task in self.config[modules_key]:
            self.learn(task, module=self.config[modules_key][task])

        if self.services_enabled:
            services_key = 'DOSAKU_SERVICES_LOAD_ON_INIT'
            for task in self.config[services_key]:
                self.learn(task, module=self.config[services_key])
