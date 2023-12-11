from dataclasses import dataclass, field
import os
from PIL.Image import Image
from typing import List, Optional

from dosaku.types import Chapter


@dataclass
class Book:
    title: Optional[str] = None
    cover: Optional[Image] = None
    chapters: List[Chapter] = field(default_factory=list)

    @property
    def chapter_lengths(self):
        return [chapter.num_words for chapter in self.chapters]

    @property
    def num_words(self):
        return sum(self.chapter_lengths)

    @property
    def illustrations(self):
        images = []
        for chapter in self.chapters:
            images += chapter.illustrations
        return images

    def __str__(self):
        text = ''
        for chapter in self.chapters:
            text += chapter.text + '\n\n'
        return text

    def save(self, dir: str):
        os.makedirs(dir, exist_ok=True)
        with open(os.path.join(dir, 'story.txt'), 'w') as file:
            file.write(str(self))
        for chapter_idx, chapter in enumerate(self.chapters):
            for image_idx, image in enumerate(self.illustrations):
                image_filename = os.path.join(dir, f'chapter{chapter_idx}_image{image_idx}.png')
                image.save(image_filename)
            audio_filename = os.path.join(dir, f'audio_{chapter_idx}.mp3')
            chapter.audio.write(filename=audio_filename)
