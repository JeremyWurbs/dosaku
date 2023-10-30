from dataclasses import dataclass, field
from PIL.Image import Image
from typing import List, Optional, Union

from dosaku import Module
from dosaku.modules import ClipdropTextToImage, OpenAIChat, BARTSummarizer
from dosaku.tasks import Chat, TextToImage, TextSummarization
from dosaku.utils import ifnone


class BookIllustrator(Module):
    """Write and illustrate short novels.

    Example::

        from dosaku.modules import BookIllustrator

        desc = ('A Naruto fanfiction focused on Shikamaru and Temari. They are tasked with overseeing the Chunin '
                'exams. During the exams, Obito, on secret orders from Madara, infiltrates the exams to kidnap a '
                'powerful examinee, whose powers are unknown to the rest of the characters. Shikamaru and Temari must '
                'team up to hunt down Obito and save the incapacitated captive.')
        creator = BookIllustrator()

        drafts = creator.gen_story(prompt=desc, word_length=2000, num_chapters=4, return_intermediate_drafts=True)
        drafts[-1] = creator.summarize_chapters(drafts[-1])
        drafts[-1] = creator.illustrate_book(drafts[-1])

        illustrated_book = drafts[-1]

    """
    name = 'BookIllustrator'

    def __init__(
            self,
            chat: Optional[Chat] = None,
            summarizer: Optional[TextSummarization] = None,
            text_to_image: Optional[TextToImage] = None):
        super().__init__()
        self.author = ifnone(chat, default=OpenAIChat(stream=False))
        self.summarizer = ifnone(summarizer, default=BARTSummarizer())
        self.illustrator = ifnone(text_to_image, default=ClipdropTextToImage())

    @dataclass
    class Book:
        chapters: List[str] = field(default_factory=list)
        chapter_summaries: List[str] = field(default_factory=list)
        illustrations: List[Image] = field(default_factory=list)

        @property
        def chapter_lengths(self):
            return [len(chapter.split(' ')) for chapter in self.chapters]

        @property
        def num_words(self):
            return sum(self.chapter_lengths)

        def __str__(self):
            text = ''
            for chapter in self.chapters:
                text += chapter + '\n\n'
            return text

    def split_draft_into_chapters(self, draft: str, num_chapters: Optional[int] = None) -> List[str]:
        chapters = draft.split('Chapter')[1:]
        for i in range(len(chapters)):
            chapters[i] = 'Chapter' + chapters[i]
        if num_chapters is not None:
            if len(chapters) < num_chapters:
                chapter_length = int(len(draft) / num_chapters)
                chapters = ['Chapter' + draft[i:i + chapter_length] for i in range(0, len(draft), chapter_length)]
        return chapters

    def gen_story(
            self,
            prompt: str,
            word_length: int = 1500,
            num_chapters: int = 3,
            num_revisions: int = 5,
            return_intermediate_drafts: bool = False
    ) -> Union[Book, List[Book]]:
        """Creates a story following the given prompt"""
        prompt = (
            f'Create a {word_length} word story about the following prompt. Be as detailed and specific as possible. '
            f'Break the story into {num_chapters} distinct chapters. Write the words "Chapter 1: [Title]", etc. '
            f'at the start of each chapter. The prompt is: {prompt}')

        draft = self.author.message(prompt)
        chapters = self.split_draft_into_chapters(draft, num_chapters=num_chapters)
        book_draft = BookIllustrator.Book(chapters=chapters)

        drafts = list()
        if return_intermediate_drafts:
            drafts.append(book_draft)

        cur_draft = 0
        while cur_draft < num_revisions:
            system_prompt = (
                f'You are an expert editor helping rewrite a short novel. You will be given a novel prompt, a '
                f'chapter draft, and comments on how to edit the chapter. You should rewrite (copy and make '
                f'appropriate edits) the chapter.'
            )
            if book_draft.num_words < int(0.9 * word_length):
                revision = list()
                for chapter in chapters:
                    self.author.reset_chat(system_prompt=system_prompt)
                    revision_prompt = (
                        f'You are an expert editor helping rewrite a book.\n'
                        f'\n'
                        f'Rewrite the following chapter to be more detailed. This chapter is {len(chapter.split(" "))} '
                        f'words long, but the target length for this chapter should be {word_length/num_chapters} '
                        f'words.\n'
                        f'\n'
                        f'The original prompt was: {prompt}\n'
                        f'\n'
                        f'The original chapter is copied below:\n\n{chapter}\n\n')
                    revision.append(self.author.message(revision_prompt))
            elif book_draft.num_words > int(1.5 * word_length):
                revision = list()
                for chapter in chapters:
                    self.author.reset_chat(system_prompt=system_prompt)
                    revision_prompt = (
                        f'You are an expert editor helping rewrite a book.\n'
                        f'\n'
                        f'Rewrite the following chapter to be more concise. This chapter is {len(chapter.split(" "))} '
                        f'words long, but the target length for this chapter should be {word_length/num_chapters} '
                        f'words.\n'
                        f'\n'
                        f'The original prompt was: {prompt}\n'
                        f'\n'
                        f'The original chapter is copied below:\n\n{chapter}\n\n')
                    revision.append(self.author.message(revision_prompt))
            elif len(draft.split('Chapter')) < num_chapters + 1:
                self.author.reset_chat(system_prompt=system_prompt)
                revision_prompt = (
                    f'You are an expert editor helping rewrite a book.\n'
                    f'\n'
                    f'Rewrite the following draft to be split into discrete chapters. You should split the text into '
                    f'{num_chapters} chapters. Each should chapter should have a title of the following form: '
                    f'"Chapter 1: [Title]".'
                    f'\n'
                    f'The original draft is copied below:\n\n{draft}\n\n')
                revision = self.author.message(revision_prompt)
                revision = self.split_draft_into_chapters(draft=revision)
            else:
                break

            book_draft = BookIllustrator.Book(chapters=revision)

            if return_intermediate_drafts:
                drafts.append(book_draft)

            cur_draft += 1

        if return_intermediate_drafts:
            drafts.append(book_draft)
            return drafts
        else:
            return book_draft

    def summarize_chapters(self, book: Book) -> Book:
        for chapter in book.chapters:
            summary = self.summarizer(text=chapter, min_length=30, max_length=800)
            book.chapter_summaries.append(summary)

    def illustrate_book(self, book: Book) -> Book:
        for summary in book.chapter_summaries:
            image = self.illustrator.text_to_image(prompt=summary)
            book.illustrations.append(image)
        return book

    def create_illustrated_book(
        self,
        prompt: str,
        word_length: int = 1500,
        num_chapters: int = 3,
        num_revisions: int = 3
    ) -> Book:
        book = self.gen_story(prompt=prompt, word_length=word_length, num_chapters=num_chapters, num_revisions=num_revisions)
        book = self.summarize_chapters(book)
        book = self.illustrate_book(book)
        return book


BookIllustrator.register_action('gen_story')
BookIllustrator.register_action('summarize_chapters')
BookIllustrator.register_action('illustrate_book')
BookIllustrator.register_action('create_illustrated_book')
BookIllustrator.register_task('BookIllustrator')
