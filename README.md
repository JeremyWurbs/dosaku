# Dosaku

Open-source, personal AI assistant.

# Installation

Create a virtual environment, and then install all the dependencies.

```commandline
pip install -r requirements.txt
```

# Usage

The main personal AI agent class is *Dosaku*.

```python
from dosaku import Dosaku

dosk = Dosaku()
```

You can see what your agent can do with:

```python
print(f'Known tasks: {dosk.tasks}')
```

Which will print a notably empty list :( 

Fortunately, your agent can learn! To see what your agent can learn:

```python
print(f'Learnable tasks: {dosk.learnable_tasks}')
```

Which will print a notably longer list. To learn one of the tasks:

```python
dosk.learn('SongSerializer')
print(f'Known tasks: {dosk.tasks}')
```

Which will now print `SongSerializer`. The `SongSerializer` task is defined in 
[dosaku.tasks.song_serializer.py](dosaku/tasks/song_serializer.py). This class defines a number of abstract methods 
which must be implemented by any class claiming to be a "SongSerializer". As we were able to learn this task, we must 
have something able to do these methods. You may test this with the following:

```python
from dosaku import Dosaku
from dosaku.tasks.song_serializer import Song

song = Song(song_id='1', title='Billie Jean', artist='Michael Jackson')
dosk = Dosaku()

dosk.SongSerializer.serialize(song)  # AttributeError: 'Agent' object has no attribute 'SongSerializer'
dosk.learn('SongSerializer')
dosk.SongSerializer.serialize(song)  # '{"id": "1", "title": "Billie Jean", "artist": "Michael Jackson"}'
```
