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

    @classmethod
    @abstractmethod
    def __call__(cls, song: Song) -> str:
        """Utility method to call serialize()."""
        raise NotImplementedError


SongSerializer.register_task()
