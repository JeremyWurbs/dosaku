# Dosaku

An open-source, personal AI assistant.

# Installation

Create a virtual environment, and then install all the dependencies.

```commandline
pip install -r requirements.txt
```

# Usage

## Quickstart

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

## Tasks and Modules

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

JsonSerializer is a class defined in [json_serializer.py](dosaku/modules/dosaku/json_serializer.py) that has registered 
itself as handling the *SongSerializer* task. That is, the JsonSerializer class implements the actual code necessary to 
do all the abstract methods for SongSerializer (in this simple example, just the *serialize* method). 

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

## Services

Services are modules that are run through the interwebs. OpenAI's ChatGPT is a service, as is Stability AI's Clipdrop
(image generation) API. 

To use services, you must provide the appropriate API keys in your [config.ini](dosaku/config/config.ini) file. To 
use Stable Diffusion through Clipdrop, for example, first go to [https://clipdrop.co/apis](https://clipdrop.co/apis),
sign up and obtain an API key. Place this key in your config file under the CLIPDROP API key. You can access this API 
key programmatically with the following:

```python
from dosaku import Config

config = Config()
config['API_KEYS']['CLIPDROP']  # Should show your API key
```

Once your API key is set up, you may enable Dosaku to use services with:

```python
from dosaku import Dosaku

dosk = Dosaku()
dosk.learn('TextToImage', module='ClipdropTextToImage')  # RuntimeError
```

Which will throw an error by default: 

```text 
Loaded module was a service, but services have not been enabled. Enable services or load a non-service module.
```

This error message is very important. When you use services, you are implicitly agreeing to:

    1. Send your data over the interwebs;
    2. You are probably spending money;

Because of these facts, services and modules are kept distinct within Dosaku.

Comparing Modules and Services:

|                                                       | Modules | Services  |
|------------------------------------------------------:|:-------:|:---------:|
|                  May download data from the interwebs |    x    |     x     |
| May run code from the interwebs on your local machine |    x    |     x     |
|                        May send data to the interwebs |         |     x     |
|                                        May cost money |         |     x     |
|                                  Computation location |  Local  | Interwebs |

In general, only use modules you trust, as they are likely downloading data (AI models with associated weights) to your
machine, where they will subsequently run. And, definitely, only use services you trust and understand how much money 
using them costs. There are no limits within Dosaku itself— so before you request a million images from the Clipdrop
service, it would be a good idea to [look at their pricing](https://clipdrop.co/apis/pricing). Currently, processing a
single text-to-image request is approximately 10 cents (USD 0.10) after any initial free credits. 

With that, in order to continue, you may enable services and learn text-to-image with:

```python
dosk.enable_services()
dosk.learn('TextToImage', module='ClipdropTextToImage')
image = dosk.TextToImage.text_to_image('Dosaku playing a game of go')
image.show()
```

Which should show a lovely image of our namesake Dosaku, as generated by Stability AI's Stable Diffusion API.

![Dosaku playing go](resources/dosaku.png)
