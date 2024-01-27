import datetime as dt

import discord
from discord.ext import commands
from discord.ext.commands import Context

from base.texts import Help
from utils.utils import display_notification
import global_const


@commands.command(
    aliases=global_const.COMMANDS_ALIASES["shutdown"],
    description=Help.SHUTDOWN,
)
@commands.is_owner()
async def shutdown(ctx: Context) -> None:
    await display_notification(ctx, "Goodbye.")
    exit()


@commands.command(
    aliases=global_const.COMMANDS_ALIASES["say_datetime"],
    description=Help.DATETIME,
)
async def say_datetime(ctx: Context) -> None:
    datetime_msg = dt.datetime.now(global_const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await display_notification(ctx, datetime_msg)


@commands.command(aliases=global_const.COMMANDS_ALIASES["display_help"])
async def display_help(ctx: Context) -> None:
    embed = discord.Embed(
        title="Bot",
        description=Help.HELP,
        color=0x00FF00,
    )
    embed.add_field(
        name="!help_reminders",
        value=Help.REMINDERS,
        inline=False,
    )
    embed.add_field(
        name="!say_datetime",
        value=Help.DATETIME,
        inline=False,
    )
    embed.add_field(
        name="!shutdown",
        value=Help.SHUTDOWN,
        inline=False,
    )
    await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(shutdown)
    bot.add_command(say_datetime)
    bot.add_command(display_help)
