import datetime as dt

import discord
from discord.ext import commands
from discord.ext.commands import Context

from base.utils import display_notification
import global_const


@commands.command(
    aliases=global_const.COMMANDS_ALIASES["shutdown"], description="Shuts down the bot."
)
@commands.is_owner()
async def shutdown(ctx: Context) -> None:
    """
    Shuts down the bot.
    """
    await display_notification(ctx, "Goodbye.")
    exit()


@commands.command(
    aliases=global_const.COMMANDS_ALIASES["say_datetime"],
    description="Says the current date and time.",
)
async def say_datetime(ctx: Context) -> None:
    """
    Says the current date and time.
    """
    datetime_msg = dt.datetime.now(global_const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await display_notification(ctx, datetime_msg)


@commands.command(aliases=global_const.COMMANDS_ALIASES["help"])
async def help(ctx: Context) -> None:
    """
    Displays information about the bot and its commands.
    """
    embed = discord.Embed(
        title="Bot",
        description="Hi! I'm a bot. I can remind you of stuff! You can mention me or use '!' prefix.\nCommands list:",
        color=0x00FF00,
    )
    embed.add_field(
        name="!help_reminders",
        value="Use when you want to know something about reminders.",
        inline=False,
    )
    embed.add_field(
        name="!say_datetime",
        value="Use when you want to see current date and time.",
        inline=False,
    )
    embed.add_field(
        name="!shutdown",
        value="Use when you want to shut down the bot. Owner-only command.",
        inline=False,
    )
    await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(shutdown)
    bot.add_command(say_datetime)
    bot.add_command(help)
