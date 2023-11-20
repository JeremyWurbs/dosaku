# Installation Instructions

## Audio support

If you wish to load or save audio (mp3) files, make sure ffmpeg is installed:

```commandline
sudo apt install ffmpeg
```

## Discord

Refer to the official [discord.py](https://github.com/Rapptz/discord.py) documentation for requirements on setting up 
your environment for connecting to discord. Most likely the only additional steps required will be installing the 
packages necessary for supporting voice, if desired. For example, for Ubuntu install `libffi-devel` and `python-dev`
with something like:

```commandline
sudo apt install libffi-dev python3.10-dev
```

Noting to match the python version to the one you are using.

# Setup

## Dosaku Configuration

Package-level Dosaku configuration is handled through [config.ini](dosaku/config/config.ini). 

The most important config values are the API keys related to any service (OpenAI, Huggingface, etc) that you wish to 
use. As these keys are effectively passwords directly connected to your credit card, it is important never to place 
these keys directly into your code. Instead, place your API keys into your config.ini file and use the Config class, 
outlined below.

### The Config Class

You can get programmatic access to your config.ini file with:

```python
from dosaku import Config

config = Config()
config['API_KEYS']['OPENAI']  # Should display the OpenAI key placed in config.ini
```

The [Config](dosaku/config/config.py) class is a wrapper around python's 
[ConfigParser](https://docs.python.org/3/library/configparser.html). If you are writing your own modules, the 
[DosakuBase](dosaku/core/dosaku_base.py) class initializes a Config object, which you may use as follows:

```python
import openai
from dosaku import Module

class MyNewModule(Module):
    def __init__(self):
        super().__init__()
        self.client = openai.Client(api_key=self.config['API_KEYS']['OPENAI'])  # Use self.config if subclassing Module
        ...
```

## Server

Refer to the backend app example for full usage. In short, you can launch a backend server with:

```commandline
gunicorn -w 1 -k uvicorn.workers.UvicornWorker apps.backend.server:app
```