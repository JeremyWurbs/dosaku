# Dosaku

An open-source, personal AI assistant.

# Quickstart Preview

1. Download Dosaku:

```commandline
git clone git@github.com:dosakunet/dosaku
```

2. Make a virtual environment as desired, and then install Dosaku:

```commandline
[mkvirtualenv dosaku]
cd dosaku
python setup.py install
```

3. Get an OpenAI API key from [https://openai.com/](https://openai.com/), and put it in your Dosaku 
[config.ini](dosaku/config/config.ini) file under API_KEYS/OPENAI.

Then launch Dosaku from the command line with:

```commandline
dosaku_gui
```

![Dosaku Chat](resources/chat_sample.png)

# Why Dosaku?

The field of AI agents is exploding. OpenAI is currently leading in technical capability, but there will be others soon
clamouring to the top— Google, Apple, X. It seems likely that all of these companies will develop closed-source, 
cloud-based agent components. Dosaku is an open-source effort to make all of these individual components accessible and 
compatible within a single framework. 

Another major aim of the project is to help modularize AI agents such that developers may roll their own agent 
applications, copyright and dependency free. That is, as open-source equivalents of top AIs become more widely 
available, Dosaku seeks to enable drop-in replacement.

Specifically, the goals of Dosaku are:

1. Provide a single open-source framework to define an interface into the major AI player services;
2. Enable plug-in-play replacements for local AI components;
3. Help support the open-source community develop and safely distribute the benefits of AGI AI agents.

# Discord AI Assistant

Dosaku is set up to be a discord AI assistant right out of the box!

To add Dosaku (or your own custom version) to your discord server:

1. Follow the online [discord documentation](https://discordpy.readthedocs.io/en/stable/discord.html) to create an 
official discord bot and invite it to your discord server.
2. Install dosaku. 
```commandline
git clone git@github.com:DosakuNet/dosaku.git && cd dosaku
python setup.py install
```
3. Copy/paste any desired API keys into your [config.ini](dosaku/config/config.ini) file. 

    i. *Discord*. Go to your bot application (from the 
[discord developer portal](https://discord.com/developers/applications)), navigate to the `Bot` tab and copy/paste the 
given bot token to your config.ini file. 

    ii. *OpenAI*. By default, Dosaku relies on OpenAI's GPT for much of its processing. To enable chat and chat related 
features, place an OpenAI API key into your config.ini file.

    iii. *Stability AI*. By default, image generation will use Stability AI's Stable Diffusion API, Clipdrop. To enable 
text-to-image and related features, place a Stability AI API key into your config.ini file.

    iv. *HuggingFace*. It is possible to replace any external API function call with a local module using models 
downloaded from HuggingFace. To do so, place a [Huggingface](https://huggingface.co/) API key into your config.ini file 
and refer to the advanced documentation section on how to run individual modules locally. 

4. Start the dosaku server backend. The server is a fastapi app that runs the default Dosaku 
[Server](dosaku/backend/server.py) class, which accepts any agent or class that implements the 
[BackendAgent](dosaku/backend/backend_agent.py) protocol to handle agent requests.
```commandline
python -m gunicorn -w 1 -b localhost:8080 -k uvicorn.workers.UvicornWorker apps.backend.server:app
```
5. Start the discord bot daemon. This daemon uses the `discord.py` package to receive and handle requests from your 
discord bot. Any AI-related requests are sent to the backend server, where they are queued and returned as they are 
processed.
```commandline
python apps/backend/discord_client.py --host localhost:8080/
```

Your bot should now be up and running!


# Contributing

You are encouraged to contribute! For information on contributing, refer to the [contrib readme](contrib.md).
