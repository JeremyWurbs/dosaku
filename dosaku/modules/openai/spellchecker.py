from typing import List, Optional

import openai

from dosaku import Config, Service
from dosaku.modules import OpenAIChat
from dosaku.utils import ifnone


class Spellchecker(Service):
    name = 'Spellchecker'
    config = Config()

    def __init__(self, model: Optional[str] = None, key_terms: Optional[List[str]] = None):
        openai.api_key = self.config['API_KEYS']['OPENAI']
        self.model = ifnone(model, self.config['OPENAI']['DEFAULT_MODEL'])
        if key_terms is None:
            key_terms = ['Dosaku']
        else:
            if 'Dosaku' not in key_terms:
                key_terms.append('Dosaku')
        self.system_prompt = (
            'You are a helpful assistant for the AI bot, Dosaku. Your task is to correct any spelling discrepancies in '
            f'the transcribed text. Make sure that the following terms are spelled correctly: {", ".join(key_terms)}. '
            'Only add necessary punctuation such as periods, commas and capitalization, and use only the context '
            'provided.')

    def spellcheck(self, text: str):
        conversation = OpenAIChat(system_prompt=self.system_prompt, model=self.model)
        return conversation.message(text)

    def __call__(self, text: str):
        return self.spellcheck(text)


Spellchecker.register_action('spellcheck')
Spellchecker.register_action('__call__')
Spellchecker.register_task('Spellchecker')
