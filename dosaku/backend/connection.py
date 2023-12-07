import json
from PIL.Image import Image
import requests
from typing import List

from dosaku.types import Message
from dosaku.utils import ascii_to_pil


class Connection:
    def __init__(self, host: str = 'http://localhost:8080/'):
        self.host = host

    def list_commands(self) -> List[str]:
        response = requests.request('POST', self.host + 'list-commands')
        return json.loads(response.content)['commands']

    def chat(self, text: str) -> Message:
        print(f'Connection posting to {self.host + "chat"}')
        response = requests.request('POST', self.host + 'chat', json={'text': text})
        print(f'chat response: {response}')
        data = json.loads(response.content)
        return Message(sender=data['sender'], text=data['text'])

    def text_to_image(self, prompt: str) -> Image:
        response = requests.request('POST', self.host + 'text-to-image', json={'prompt': prompt})
        image_data = json.loads(response.content)['image']
        return ascii_to_pil(image_data)
