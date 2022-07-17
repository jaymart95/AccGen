import logging
from asyncio import sleep
from datetime import datetime
from pathlib import Path

import config
import disnake
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from disnake import Embed, Intents
from disnake.errors import Forbidden
from disnake.ext.commands import BadArgument
from disnake.ext.commands import Bot as Jump
from disnake.ext.commands import (CommandNotFound, Context,
                                  MissingRequiredArgument)
from disnake.ext.commands.bot import when_mentioned_or
from disnake.ext.commands.errors import CommandOnCooldown, MissingPermissions
from lib.db import db

PREFIX = '!'
OWNER_ID = [485183782328991745]
cogs = [p.stem for p in Path('.').glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)
intents= disnake.Intents(guilds=True, presences=True, members=True)

def get_prefix(bot, message):
    return when_mentioned_or(PREFIX)(bot, message)


class Ready(object):
    def __init__(self):
        for cog in cogs:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        logging.info(f'{cog} cog ready')

    def all_ready(self):
        return all([getattr(self, cog) for cog in cogs])


class Bot(Jump):
    def __init__(self):
        self.PREFIX = PREFIX
        self.cogs_ready = Ready()
        self.scheduler = AsyncIOScheduler()
        self.ready = False

        super().__init__(
            command_prefix=get_prefix,
            owner_id=OWNER_ID,
            intents=intents,
        )

    def setup(self):
        for cog in cogs:
            self.load_extension(f'lib.cogs.{cog}')
            logging.info(f'{cog} cog loaded')

        logging.info('setup complete')

    def run(self, version):
        self.VERSION = version
        print('Running setup...')
        self.setup()

        self.TOKEN = config.TOKEN

        print('running bot....')
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send('Im not ready to receive commands. Please wait!!')

    async def on_connect(self):
        logging.info('bot connected')

    async def on_disconnect(self):
        logging.info('bot disconnect')

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            self.bot = bot

            while not self.cogs_ready.all_ready():
                await sleep(0.3)

            self.ready = True
            logging.info('bot ready')

        else:
            logging.info('bot reconnect')

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
