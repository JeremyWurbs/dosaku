# Dosaku

An open-source, personal AI assistant.

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
dosk.tasks  # []
```

Which will print a notably empty list :( 

Fortunately, your agent can learn! To see what your agent can learn:

```python
dosk.learnable_tasks  # ['SongSerializer', ...]
```

Which will print a notably longer list. To learn one of the tasks:

```python
dosk.learn('SongSerializer')
dosk.tasks  # ['SongSerializer']
```

Which will now print `SongSerializer`. The `SongSerializer` task is defined in 
[dosaku.tasks.song_serializer.py](dosaku/tasks/song_serializer.py). This class defines one or more abstract methods 
which must be implemented by any class claiming to be a "SongSerializer" (in this case, it defines a single abstract 
method, *serialize*). As we were able to learn this task, we must have something able to do *serialize*. You may test 
this hypothesis with the following:

```python
from dosaku import Dosaku
from dosaku.tasks.song_serializer import Song

song = Song(song_id='1', title='Billie Jean', artist='Michael Jackson')
dosk = Dosaku()

dosk.SongSerializer.serialize(song)  # AttributeError: 'Agent' object has no attribute 'SongSerializer'
dosk.learn('SongSerializer')
dosk.SongSerializer.serialize(song)  # '{"id": "1", "title": "Billie Jean", "artist": "Michael Jackson"}'
```

# Tasks and Modules

Dosaku is meant to bridge the world of humans and AI. As such, there are two fundamental *spaces* which define the key 
concepts to the Dosaku platform: *tasks* and *modules*.

Tasks live in the human space. They are the things we want our AI assistant to be able to do: "*play chess*", "*extract 
the text from a pdf document*", "*text-to-image*" (i.e. create an image given a text prompt). Each of these *Tasks* 
takes a human concept and defines an explicit API. The task, "play go" (go-- the ancient chess-like board game), for 
example, can be explicitly defined by the [go text protocol](https://en.wikipedia.org/wiki/Go_Text_Protocol). Any 
computer agent which follows this protocol can, for instance, be used to connect and play on the popular go server 
[KGS](http://gokgs.com/). In this case, "play go" is a human-decipherable Task which defines a computer API interface.

In the above example, we learned the Task *SongSerializer*, which was defined as an abstract class. As you may know, 
abstract classes do not define the actual implementation and, at least in python, cannot even be instantiated. You may 
ask, what is actually *doing* the work then? What is it that we actually asked Dosaku to "learn". 

The answer is a Module.

Modules live in the machine space. They are programs that do *something*. Modules can be anything, really. To be used by
Dosaku, however, they must register (i.e. claim that they can do) at least one Task. When we ask Dosaku to 
*learn* something, what we are doing is asking Dosaku to load (download, install, load into memory, etc.) a Module 
*program* able to do the *Task*. Later, when Dosaku does the *Task*, what it is actually doing is running the *Module* 
program. 

Following the above SongSerializer example, you can see what Module was loaded with:

```python
dosk.loaded_modules  # ['JsonSerializer']
```

Which will yield *JsonSerializer*. JsonSerializer is a class defined in 
[json_serializer.py](dosaku/modules/dosaku/json_serializer.py) that has registered itself as handling the task 
*SongSerializer*. That is, the JsonSerializer class implements the actual code necessary to do all the abstract methods
for SongSerializer (in this simple example, just the *serialize* method). 

But JsonSerializer is not the only possible option. You may list all the Modules that have registered themselves as 
implementing a given Task with:

```python
dosk.registered_modules('SongSerializer')  # ['JsonSerializer', 'XmlSerializer', 'YamlSerializer']
```

To learn (load, run) a different Module, we can pass it in explicitly when we learn the task:

```python
dosk.learn('SongSerializer', module='XmlSerializer')
dosk.SongSerializer.serialize(song)  # '<song id="1"><title>Billie Jean</title><artist>Michael Jackson</artist></song>'
```

Note that JsonSerializer and XmlSerializer are **not** equivalent. The only promise they have made is that they define 
a method, *serialize*, which takes a *Song* object and returns a string. In this case, one yields a json-formatted 
string and one an xml-formatted string. In general, anything not explicitly defined by the Task API must be checked by 
the user to make sure their agent is learning the right things. 
