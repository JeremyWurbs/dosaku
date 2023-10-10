import openai

from dosaku import Config, Service


class Ponder(Service):
    name = 'WriteModule'
    config = Config()

    def __init__(self):
        openai.api_key = self.config['API_KEYS']['OPENAI']

    def write_task(self, context: str, task_reqs: str, examples: str, **kwargs):
        pass

    def write_module(self, context: str, module_reqs: str, examples: str, **kwargs):
        pass


Ponder.register_task('WriteTask')
Ponder.register_task('WriteModule')
