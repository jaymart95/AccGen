import disnake
from disnake import SyncWebhook
from disnake.ext.commands import Cog, has_permissions
from lib.db import db
from disnake.ext.commands.slash_core import slash_command
from disnake.ext import tasks

class Events(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('Events')

    @Cog.listener()
    async def on_guild_join(self, guild):

        db.execute("INSERT INTO guild (GuildID) VALUES (?)", guild.id)

        db.commit()

    @Cog.listener()
    async def on_guild_leave(self, guild):
        db.execute("DELETE FROM guild WHERE GuildID = ?", guild.id)

        db.commit()

    
    @Cog.listener()
    async def on_member_join(self, member):
        db.execute("INSERT INTO members (userID) VALUES (?)", member.id)

        db.commit()

    @Cog.listener()
    async def on_member_remove(self, member):
        db.execute("DELETE FROM members WHERE MemberID = ?", member.id)

        db.commit()


    @tasks.loop(seconds=30)
    async def role_check(self):
        for member in self.bot.guilds.members:
            time = db.field("SELECT rTIime FROM members WHERE userID = ?", member.id)
            if time == "None":
                continue
            elif time < time.now():
                db.execute("UPDATE members SET rTime = ? WHERE userID = ?", "None", member.id)
                db.commit()
                await member.remove_roles(member.guild.get_role(db.field("SELECT roleID FROM members WHERE userID = ?", member.id)))
                db.execute("DELETE FROM members WHERE userID = ?", member.id)
                db.commit()
    

def setup(bot):
    bot.add_cog(Events(bot))
