import xml.etree.ElementTree as et

from dosaku import Module
from dosaku.tasks.song_serializer import Song


class XmlSerializer(Module):
    name = 'XmlSerializer'

    def __init__(self):
        super().__init__()

    def serialize(self, song: Song) -> str:
        song_info = et.Element('song', attrib={'id': song.song_id})
        title = et.SubElement(song_info, 'title')
        title.text = song.title
        artist = et.SubElement(song_info, 'artist')
        artist.text = song.artist
        return et.tostring(song_info, encoding='unicode')

    def __call__(self, song: Song) -> str:
        return self.serialize(song)


XmlSerializer.register_action('__call__')
XmlSerializer.register_task('SongSerializer')
