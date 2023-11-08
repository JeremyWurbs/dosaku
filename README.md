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

# Contributing

You are encouraged to contribute! For information on contributing, refer to the [contrib readme](contrib.md).

