import datetime as dt

from discord.ext import commands
from discord.ext.commands import Context

from utils.utils import display_notification
import global_const


@commands.command(
    aliases=global_const.COMMANDS_ALIASES["shutdown"],
    description="Shuts the bot down.",
)
@commands.is_owner()
async def shutdown(ctx: Context) -> None:
    await display_notification(ctx, "Goodbye.")
    exit()


@commands.command(
    aliases=global_const.COMMANDS_ALIASES["say_datetime"],
    description="Says the current date and time.",
)
async def say_datetime(ctx: Context) -> None:
    datetime_msg = dt.datetime.now(global_const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await display_notification(ctx, datetime_msg)


async def setup(bot):
    bot.add_command(shutdown)
    bot.add_command(say_datetime)
