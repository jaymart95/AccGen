import asyncio
import datetime
import typing
from typing import Optional
from unicodedata import category
import disnake
from disnake.ext.commands import Cog, has_permissions, Param, cooldown, BucketType, has_any_role
from disnake.ext.commands.slash_core import slash_command
from lib.db import db
from lib.utils.helpers import get_random_string
from disnake.ext import tasks

class Commands(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('Commands')
    
    @slash_command(name="key_gen", default_member_permissions=disnake.Permissions(administrator=True))
    async def key_generator(self, inter, amount: int):
        """
        Generate redeemable keys

        Parameters
        ----------
        amount: The amount of keys you want to generate
        """
        if amount < 1:
            return await inter.send("You need to specify a number greater than 0")
        get_random_string(amount)
        
        await inter.send(f"Successfully generated {amount} keys", ephemeral=True)

    @slash_command(name="redeem")
    async def redeem_key(self, inter, key: str):
        """
        Redeem a key

        Parameters
        ----------
        key: The key you want to redeem
        """
        role = inter.guild.get_role(996256479990513734)
        if len(key) < 1:
            return await inter.send("You need to specify a key")
        keys = db.column("SELECT * FROM access_keys")
        if key in keys:
            db.execute("DELETE FROM access_keys WHERE access_key = ?", key)
            db.commit()
            await inter.author.add_roles(role)
            await inter.send("Successfully redeemed key", ephemeral=True)
            embed = disnake.Embed(title="Key Redeemed", description=f"{inter.author.mention} has redeemed a key", color=0x00ff00)

            embed.set_footer(text=inter.author, icon_url=inter.author.avatar.url)

        else:
            await inter.send("Invalid key.", ephemeral=True)

    @slash_command(name="key_list", default_member_permissions=disnake.Permissions(administrator=True))
    async def key_list(self, inter):
        """
        List all redeemable keys
        """
        keys = db.record("SELECT * FROM access_keys")
        if len(keys) < 1:
            return await inter.send("There are no keys")
        await inter.send("```\n" + "\n".join(keys) + "```", ephemeral=True)

    @slash_command(name="key", default_member_permissions=disnake.Permissions(administrator=True))
    async def key(self, inter, member: disnake.Member, duration: typing.Literal["1d", "3d", "7d", "30d", "Lifetime"]):
        """
        Give a user a key

        Parameters
        ----------
        member: The user you want to give a key to
        duration: The duration of the key
        """
        if duration == "1d":
            duration = datetime.datetime.now() + datetime.timedelta(days=1)
        elif duration == "3d":
            duration = datetime.datetime.now() + datetime.timedelta(days=3)
        elif duration == "7d":
            duration = datetime.datetime.now() + datetime.timedelta(days=7)
        elif duration == "30d":
            duration = datetime.datetime.now() + datetime.timedelta(days=30)
        elif duration == "Lifetime":
            duration = datetime.datetime.now() + datetime.timedelta(days=999999)
        else:
            return await inter.send("Invalid duration.")
        key = db.field("SELECT * FROM access_keys ORDER BY RANDOM() LIMIT 1")
        check = db.field("SELECT userID FROM members WHERE userID = ?", member.id)
        if check is None:
            db.execute("INSERT INTO members (userID, rTime) VALUES (?, ?)", member.id, duration)
            db.commit()
            await member.send(f"You have received a key. Expiration: {duration}.\n\n{key}")
            await inter.send(f"Successfully gave {member.mention} a key. Expiration: {duration}", ephemeral=True)
        else:
            db.execute("UPDATE members SET rTime = ? WHERE UserID = ?", duration, member.id)
            db.commit()
            await member.send(f"You have received a key. Expiration: {duration}.\n\n{key}")
            await inter.send(f"Successfully gave {member.mention} a key. Expiration: {duration}", ephemeral=True)

    @slash_command(name="upload", default_member_permissions=disnake.Permissions(administrator=True))
    async def upload(self, inter, attachment: disnake.Attachment, account_type: typing.Literal["aged cod", "bnet", "phub", "spotify", "disney", "val", "hbo max", "netflix"]):
        """
        Upload accounts to the database

        Parameters
        ----------
        file: The file you want to upload
        account_type: The type of accounts you are uploading
        """
        await inter.response.defer(with_message=True, ephemeral=True)

        await attachment.save(f"./{attachment.filename}")
        with open(attachment.filename, "r") as f:
            accounts = f.read().split("\n")
        for account in accounts:
            if len(account) < 1:
                continue
            db.execute("INSERT INTO accs (account, AccountType) VALUES (?, ?)", account, account_type)
        db.commit()
        await inter.edit_original_message(content="Successfully uploaded accounts")

    @slash_command(name="account")
    @cooldown(15, 86400, BucketType.member)
    async def account(self, inter: disnake.ApplicationCommandInteraction, account_type: typing.Literal["aged cod", "bnet", "phub", "spotify", "disney", "val", "hbo max", "netflix"]):
        """
        Get a random account of a certain type

        Parameters
        ----------
        account_type: The type of account you want to get
        """
        role = inter.guild.get_role(996256479990513734)

        if role not in inter.author.roles:
            return await inter.send("You do not have permission to use this command.")

        account = db.field("SELECT * FROM accs WHERE accounttype = ? ORDER BY RANDOM() LIMIT 1", account_type)
        db.execute("DELETE FROM accs WHERE account = ?", account)
        if account is None:
            return await inter.send("No accounts of this type")
        redeems = db.field("SELECT redeems FROM members WHERE userID = ?", inter.author.id)
        log_channel = inter.guild.get_channel(1008122637987369031)
        embed = disnake.Embed(title=f"{account_type} has been generated", color=0x00ff00)
        embed.set_author(name=inter.author, icon_url=inter.author.avatar.url)
        embed.add_field(name="Daily Redeems", value=redeems)
        await log_channel.send(embed=embed)
        await inter.send(f"{account}", ephemeral=True)

    @slash_command(name="stock")
    async def stock(self, inter, account_type: typing.Literal["aged cod", "bnet", "phub", "spotify", "disney", "val", "hbo max", "netflix"]):
        """
        Get a random account of a certain type

        Parameters
        ----------
        account_type: The type of account you want to get
        """
        account = db.field("SELECT COUNT(*) FROM accs WHERE accounttype = ?", account_type)
        if account is None:
            return await inter.send("No accounts of this type")
        await inter.send(f"{account} {account_type} accounts")

    
    @slash_command(name="clear_stock", default_member_permissions=disnake.Permissions(administrator=True))
    async def clear_stock(self, inter, account_type: typing.Literal["aged cod", "bnet", "phub", "spotify", "disney", "val", "hbo max", "netflix"]):
        """
        Clear all accounts of a certain type

        Parameters
        ----------
        account_type: The type of account you want to clear
        """
        db.execute("DELETE FROM accs WHERE accounttype = ?", account_type)
        db.commit()
        await inter.send(f"Cleared {account_type} accounts")

    @tasks.loop(hours=24)
    async def redeem_reset(self):
        for member in self.bot.guild.members:
            db.execute("UPDATE members SET redeems = ? WHERE UserID = ?", 0, member.id)   



def setup(bot):
    bot.add_cog(Commands(bot))
