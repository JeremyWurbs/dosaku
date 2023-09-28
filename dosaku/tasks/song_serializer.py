from abc import abstractmethod

from dosaku import Task


class Song:
    def __init__(self, song_id, title, artist):
        self.song_id = song_id
        self.title = title
        self.artist = artist


class SongSerializer(Task):
    name = 'SongSerializer'

    def __init__(self):
        super().__init__()

    @abstractmethod
    def serialize(self, song: Song) -> str:
        raise NotImplementedError


SongSerializer.register_task()
