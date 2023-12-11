from typing import List, Optional

from dosaku import Module, Service
from dosaku.tasks import Chat, TextToImage, TextSummarization, TextToSpeech
from dosaku.modules import GPT, BARTSummarizer, ClipdropTextToImage, OpenAITextToSpeech
from dosaku.types import Chapter, Book
from dosaku.utils import ifnone


class KiteWriter(Module):
    name = 'KiteWriter'

    def __init__(
            self,
            chat: Optional[Chat] = None,
            summarizer: Optional[TextSummarization] = None,
            text_to_image: Optional[TextToImage] = None,
            text_to_speech: Optional[TextToSpeech] = None
    ):
        super().__init__()
        self.author = ifnone(chat, default=GPT())
        self.summarizer = ifnone(summarizer, default=BARTSummarizer())
        self.illustrator = ifnone(text_to_image, default=ClipdropTextToImage())
        self.orator = ifnone(text_to_speech, default=OpenAITextToSpeech())

    def create_book(self, prompt: str) -> Book:
        context = (
            'You are a professional writer, currently being paid to ghost write for a well-known academic author. Your '
            'task is to produce high quality drafts on the prompts given to you.\n'
            '\n'
            'When you response, you should respond with the requested number of paragraphs, inserting two newline '
            'characters between each paragraph. For example, given the prompt "Write me a three paragraph story '
            'about the following prompt:\n\na boy on Christmas morning, you could respond with:\n'
            '\n'
            '**The Night Before Dawn** This is the first paragraph. You might write a detailed account of how excited '
            'the boy was Christmas eve night, not going to sleep till he heard Santa come down the chimney.\n'
            '\n'
            '**The Morning Arrives** This is the second paragraph. You might write about the events of a family '
            'gathered for Christmas morning, with the boy excitedly unwrapping presents while his parents slow him '
            'down to enjoy the moment.\n'
            '\n'
            '**The Real Christmas** This is the third paragraph. You might write about the boy going out to play with '
            'his new toys only to find his neighbor is less fortunate and his family was not able to afford any gifts. '
            'The boy might share his gifts with his neighbor, learning a deeper meaning of Christmas to share joy with '
            'one another.'
        )
        response = self.author.message(
            f'Write me a five paragraph story about the following prompt:\n\n{prompt}',
            instructions=context
        )

        book = Book()
        self.logger.debug(f'Started writing book on the following prompt: {prompt}')
        for idx, text in enumerate(response.message.split('\n\n')):
            print(f'{text}\n\n')
            self.logger.debug(f'Chapter {idx}: {text}')
            summary = self.summarizer.summarize(text)
            image = self.illustrator.text_to_image(summary)
            audio = self.orator.text_to_speech(text)
            chapter = Chapter(
                text=text,
                summary=summary,
                illustrations=[image],
                audio=audio
            )
            book.chapters.append(chapter)
        return book
