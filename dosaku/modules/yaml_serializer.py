import yaml

from dosaku.modules import JsonSerializer
from dosaku.tasks.song_serializer import Song


class YamlSerializer(JsonSerializer):
    name = 'YamlSerializer'

    def serializer(self, song: Song) -> Song:
        return yaml.dump(super().serialize(song))


YamlSerializer.register_task('SongSerializer')
