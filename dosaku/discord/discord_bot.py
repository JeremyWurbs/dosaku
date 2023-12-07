from math import floor
import os
import requests
from typing import List, Optional

import discord
from discord.ext import commands

from dosaku import DosakuBase
from dosaku.utils import ifnone
from dosaku.backend import Server


class DiscordBot(DosakuBase):
    def __init__(
            self,
            host: str = 'http://localhost:8080/',
            description='Dosaku Assistant',
            command_prefixes: Optional[List[str]] = None
    ):
        super().__init__()
        self.backend_server = Server.connection(host)
        self.description = description
        self.command_prefixes = ifnone(command_prefixes, default=['>', 'dosaku '])

        self.intents = discord.Intents.default()
        self.intents.members = True
        self.intents.message_content = True

    def run(self):
        bot = commands.Bot(
            description=self.description,
            command_prefix=self.command_prefixes,
            intents=self.intents)

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
            if any([message.content.startswith(prefix) for prefix in self.command_prefixes]):
                await bot.process_commands(message)
                return

            # Else if the message is a DM maintain a standard chat convo
            if not message.guild:  # message is a DM
                try:
                    print(f'User {message.author} sent a chat query: {message.content}')
                    response = self.backend_server.chat(text=message.content)
                    max_len = 2000
                    num_chunks = max(floor(len(response.text) // max_len), 1)
                    for idx in range(num_chunks):
                        start = idx * max_len
                        end = (idx + 1) * max_len
                        await message.channel.send(response.text[start:end])
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
                        f'command prefixes: {self.command_prefixes}\n'
                        f'commands: {self.backend_server.commands()}\n\n'
                        f'For example, you may use me to generate an image with:\n'
                        f'>text_to_image An astronaut riding a horse, 4k photograph f/1.4'
                    )
                    await message.reply(response, mention_author=True)
                except discord.errors.Forbidden:
                    pass

        @bot.command()
        async def list_commands(ctx):
            await ctx.send(self.backend_server.commands())

        @bot.command()
        async def text_to_image(ctx, *, prompt: str):
            print(f'Received t2i request from user {ctx.author} with prompt: {prompt}')
            image = self.backend_server.text_to_image(prompt)
            filename = os.path.join(self.config['DIR_PATHS']['TEMP'], 'image.png')
            image.save(filename)
            await ctx.send('Sure, how about this?', file=discord.File(filename))

        @bot.command()
        async def transcribe_audio(
                ctx,
                interviewer: Optional[str] = 'Interviewer',
                interviewee: Optional[str] = 'Interviewee'
        ):
            print(f'Received transcribe_audio request from user {ctx.author}')
            attachment_url = ctx.message.attachments[0].url
            print(f'Attachment url: {attachment_url}')
            file_request = requests.get(attachment_url)
            print(f'Download response: {file_request}')
            filename = os.path.join(self.config['DIR_PATHS']['TEMP'], 'audio.mp3')
            with open(filename, 'wb') as audio_file:
                audio_file.write(file_request.content)

            transcription = self.backend_server.transcribe_interview(
                audio_file=filename,
                interviewer=interviewer,
                interviewee=interviewee
            )
            print(f'Transcription:\n\n{transcription}')
            await ctx.send(f'{transcription}')

        @bot.command()
        async def set_voice(ctx, voice: str):
            if voice is None or voice not in self.backend_server.voices():
                await ctx.send(f'I do not know that voice. Please select one of {self.backend_server.voices()}')
            else:
                self.voice = voice
                await ctx.send(f'Certainly, I\'ll use the {voice} voice from now on.')

        bot.run(self.config['API_KEYS']['DISCORD'])
