import json

from dosaku import Module
from dosaku.tasks.song_serializer import Song


class JsonSerializer(Module):
    name = 'JsonSerializer'

    def __init__(self):
        super().__init__()

    def serialize(self, song: Song) -> str:
        song_info = {
            'id': song.song_id,
            'title': song.title,
            'artist': song.artist
        }
        return json.dumps(song_info)

    def __call__(self, song: Song) -> str:
        return self.serialize(song)


JsonSerializer.register_task(task='SongSerializer')
