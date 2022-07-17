from apscheduler.triggers.cron import CronTrigger
from disnake import Activity, ActivityType, Embed
from disnake import __version__ as disnake_version
from disnake.ext.commands import Cog
from disnake.ext.commands.slash_core import slash_command


class Status(Cog):
    def __init__(self, bot):
        self.bot = bot

        self._message = "watching discord.gg/jdev"

        bot.scheduler.add_job(self.set, CronTrigger(second=0))

    @property
    def message(self):
        return self._message.format(users=len(self.bot.users), guilds=len(self.bot.guilds))

    @message.setter
    def message(self, value):
        if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
            raise ValueError("Invalid activity type.")

        self._message = value

    async def set(self):
        _type, _name = self.message.split(" ", maxsplit=1)

        await self.bot.change_presence(activity=Activity(
            name=_name, type=getattr(ActivityType, _type, ActivityType.playing)
        ))

def setup(bot):
    bot.add_cog(Status(bot))
