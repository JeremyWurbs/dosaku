from math import ceil
import os
import random
from typing import List, Optional

import discord
from PIL.Image import Image
from discord.ext import tasks, commands
import requests

from dosaku import Service
from dosaku.backend import BackendAgent
from dosaku.modules import (GPT,
                            Whisper,
                            OpenAITextToSpeech,
                            OpenAIInterviewDiarization,
                            ClipdropTextToImage,
                            BARTSummarizer,
                            KiteWriter)
from dosaku.types import Audio, Message
from dosaku.utils import bytes_to_pil


class Dosaku(Service, BackendAgent):
    name = 'Dosaku'

    def __init__(self):
        super().__init__()
        self.models = {
            'chat': GPT(),
            'text_to_image': ClipdropTextToImage(),
            'interview_transcriptionist': OpenAIInterviewDiarization(),
            'text_to_speech': OpenAITextToSpeech(),
        }

        #self.t2s = OpenAITextToSpeech()
        #self.s2t = Whisper()
        #self.summarizer = BARTSummarizer()
        #self.interview_transcriptionist = OpenAIInterviewDiarization()
        #self.kw = KiteWriter()
        #self.voice = 'alloy'

        self._busy = False
        self._command_prefixes = ['>', 'dosaku ']
        self._commands = [
            'list_commands',
            'roll',
            'choose',
            'repeat',
            'text_to_image',
            'analyze_image',
            'transcribe_audio',
            'set_voice',
            'text_to_speech',
            'gen_short_story'
        ]

    def commands(self) -> List[str]:
        return self._commands

    def chat(self, text: str) -> Message:
        return self.models['chat'].message(text)

    def text_to_speech(self, text: str) -> Audio:
        return self.models['text_to_speech'].text_to_speech(text)

    def text_to_image(self, prompt: str) -> Image:
        return self.models['text_to_image'].text_to_image(prompt)

    def transcribe_audio(self, audio: Audio) -> str:
        return 'This is not a real transcript'

    def transcribe_interview_audio(
            self,
            audio: Audio,
            interviewer: Optional[str] = None,
            interviewee: Optional[str] = None
    ) -> str:
        return 'This is not a real transcript'

    def voices(self) -> List[str]:
        return self.models['text_to_speech'].voices

    def voice(self, voice: str) -> None:
        self.models['text_to_speech'].voice = voice

    @property
    def busy(self) -> bool:
        return self._busy

    def discord_bot(self):
        description = '''An example bot to showcase the discord.ext.commands extension
                    module.

                    There are a number of utility commands being showcased here.'''

        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        bot = commands.Bot(command_prefix=self._command_prefixes, description=description, intents=intents)

        @bot.event
        async def on_ready():
            print(f'Logged in as {bot.user} (ID: {bot.user.id})')
            print('------')

        @bot.event
        async def on_message(message):
            # Make sure we do not reply to ourselves
            if message.author.id == bot.user.id:
                return

            # If the message starts with a command prefix, do the command and return
            if any([message.content.startswith(prefix) for prefix in self._command_prefixes]):
                await bot.process_commands(message)
                return

            # Else if the message is a DM maintain a standard chat convo
            if not message.guild:  # message is a DM
                try:
                    print(f'User {message.author} sent a chat query: {message.content}')
                    response = self.chat.message(text=message.content)
                    max_len = 2000
                    num_chunks = ceil(len(response.message) // max_len)
                    for idx in range(num_chunks):
                        start = idx * max_len
                        end = (idx + 1) * max_len
                        await message.channel.send(response.message[start:end])
                    if len(response.images) > 0:
                        for image in response.images:
                            filename = os.path.join(self.config['DIR_PATHS']['TEMP'], 'image.png')
                            image.save(filename)
                            with open(filename, 'rb') as image_bytes:
                                discord_image = discord.File(image_bytes)
                                await message.channel.send(file=discord_image)
                            await message.channel.send(file=filename)
                except discord.errors.Forbidden:
                    pass

            # Else if the message mentions us in some way, add a reply on how to use us.
            elif 'dosaku' in message.content.lower():
                try:
                    response = (
                        f'Hello! If you\'re trying to chat with me, you can chat with me freely by DMing me. You may '
                        f'also run any of my commands in any channel:\n\n'
                        f'command prefixes: {self._command_prefixes}\n'
                        f'commands: {self._commands}\n\n'
                        f'For example, you may use me to generate an image with:\n'
                        f'>text_to_image An astronaut riding a horse, 4k photograph f/1.4'
                    )
                    await message.reply(response, mention_author=True)
                except discord.errors.Forbidden:
                    pass

        @bot.command()
        async def list_commands(ctx):
            await ctx.send(self.commands)

        @bot.command()
        async def roll(ctx, dice: str):
            """Rolls a dice in NdN format."""
            try:
                rolls, limit = map(int, dice.split('d'))
            except Exception:
                await ctx.send('Format has to be in NdN!')
                return

            result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
            await ctx.send(result)

        @bot.command(description='For when you wanna settle the score some other way')
        async def choose(ctx, *choices: str):
            """Chooses between multiple choices."""
            await ctx.send(random.choice(choices))

        @bot.command()
        async def repeat(ctx, times: int, content='repeating...'):
            """Repeats a message multiple times."""
            for i in range(times):
                await ctx.send(content)

        @bot.command()
        async def joined(ctx, member: discord.Member):
            """Says when a member joined."""
            await ctx.send(f'{member.name} joined {discord.utils.format_dt(member.joined_at)}')

        @bot.group()
        async def cool(ctx):
            """Says if a user is cool.

            In reality this just checks if a subcommand is being invoked.
            """
            if ctx.invoked_subcommand is None:
                await ctx.send(f'No, {ctx.subcommand_passed} is not cool')

        @cool.command(name='bot')
        async def _bot(ctx):
            """Is the bot cool?"""
            await ctx.send('Yes, the bot is cool.')

        @bot.command()
        async def analyze_image(ctx):
            print(f'Received analyze_image request from user {ctx.author}')
            attachment_url = ctx.message.attachments[0].url
            print(f'Attachment url: {attachment_url}')
            file_request = requests.get(attachment_url)
            print(f'Downloaded response: {file_request}')
            image = bytes_to_pil(file_request.content)
            image.show()

        @bot.command()
        async def text_to_speech(ctx, *, text: Optional[str] = None):
            print(f'Received text_to_speech request from user {ctx.author} with text: {text}')
            filename = os.path.join(self.config['DIR_PATHS']['TEMP'], 'audio.mp3')
            self.t2s.text_to_speech(text=text, output_filename=filename, voice=self.voice)
            await ctx.send('Sure, here\'s audio for that transcript', file=discord.File(filename))

        @bot.command()
        async def gen_short_story(ctx, *, prompt: str):
            await ctx.send('Sure, I\'ll get right on that. Please be patient, this may take a moment..')
            book = self.kw.create_book(prompt)
            await ctx.send('Hello, I\'m back! I\'ve finished the first draft, what do you think of this?')
            for idx, chapter in enumerate(book.chapters):
                if idx > 5:  # Make sure we don't go crazy, for now
                    break
                for image in chapter.illustrations:
                    filename = os.path.join(self.config['DIR_PATHS']['TEMP'], 'image.png')
                    image.save(filename)
                    await ctx.send('', file=filename)
                await ctx.send(chapter.text)
                filename = os.path.join(self.config['DIR_PATHS']['TEMP'], 'audio.mp3')
                chapter.audio.write(filename)
                await ctx.send('', file=filename)

        return bot

    def connect_to_discord(self):
        bot = self.discord_bot()
        bot.run(self.config['API_KEYS']['DISCORD'])
        #try:
        #    await bot.start(self.config['API_KEYS']['DISCORD'])
        #except Exception:
        #    await bot.close()

