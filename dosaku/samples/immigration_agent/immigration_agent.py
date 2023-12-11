import glob
from math import floor
import os
import requests
from typing import Dict

import discord

from dosaku import DiscordBot
from dosaku.modules import GPT
from dosaku.types import ChatHistory, Message


class ImmigrationAgent(DiscordBot):
    def __init__(self, description='Immigration Agent', **kwargs):
        super().__init__(description=description, **kwargs)
        self.supported_commands += ['upload_pdfs']
        self.user_chat_histories: Dict[str, ChatHistory] = {}

    @classmethod
    def pdf_filenames(cls, dir_path):
        return glob.glob(os.path.join(dir_path, '*.pdf'))

    def user_dir(self, name) -> str:
        return str(os.path.join(self.config['DIR_PATHS']['DISCORD'], name))

    def discord_bot(self):
        bot = super().discord_bot()

        @bot.command()
        async def upload_pdfs(ctx):
            self.logger.debug(f'Received upload_files request from user {ctx.author}.')
            for idx, attachment in enumerate(ctx.message.attachments):
                attachment_url = attachment.url
                print(f'Attachment url: {attachment_url}')
                file_request = requests.get(attachment_url)
                user_dir = self.user_dir(ctx.author.name)
                os.makedirs(user_dir, exist_ok=True)
                filename = os.path.join(user_dir, f'file_{idx}.pdf')
                with open(filename, mode='bw') as file:
                    file.write(file_request.content)
            self.logger.debug(f'Returning upload_files request for user {ctx.author}.')
            await ctx.message.channel.send('Sure, I\'ll refer to these documents for future replies.')

        # Overwrite the on_message event from Dosaku
        bot.remove_command('on_message')
        @bot.event
        async def on_message(message):
            self.logger.debug(f'Received message from user {message.author}.')
            # Make sure we do not reply to ourselves
            if message.author.id == bot.user.id:
                return

            # If the message starts with a command prefix, do the command and return
            if any([message.content.startswith(prefix) for prefix in self.command_prefixes]):
                await bot.process_commands(message)
                return

            # Else if the message is a DM maintain a standard chat convo
            if not message.guild or True:  # message is a DM
                self.logger.debug(f'Message from {message.author} sent to free DM chat. Message: {message.content}')
                try:
                    filenames = self.pdf_filenames(self.user_dir(message.author.name))
                    if message.author.name not in self.user_chat_histories.keys():
                        self.user_chat_histories[message.author.name] = ChatHistory()
                    user_message = Message(sender='user', text=message.content)
                    self.user_chat_histories[message.author.name].add_message(user_message)

                    with GPT(filenames=filenames) as gpt:
                        # TODO: pass user chat history to GPT
                        response = gpt.message(text=message.content)

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
                    self.logger.debug(f'Returning DM message from user {message.author}.')
                except discord.errors.Forbidden as err:
                    self.logger.exception(f'Error raised in processing message from user {message.author}:\n{err}')

            # Else if the message mentions us in some way, add a reply on how to use us.
            elif 'dosaku' in message.content.lower():
                self.logger.debug(f'Message from {message.author} sent to channel chat. Message: {message.content}')
                try:
                    response = (
                        f'Hello! If you\'re trying to chat with me, you can chat with me freely by DMing me. You may '
                        f'also run any of my commands in any channel:\n\n'
                        f'command prefixes: {self.command_prefixes}\n'
                        #  f'commands: {self.commands}\n\n'
                        f'For example, you may use me to generate an image with:\n'
                        f'>text_to_image An astronaut riding a horse, 4k photograph f/1.4'
                    )
                    await message.reply(response, mention_author=True)
                    self.logger.debug(f'Returning channel message from user {message.author}.')
                except discord.errors.Forbidden:
                    pass

        return bot
