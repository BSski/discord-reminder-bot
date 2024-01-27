import datetime as dt
from datetime import timezone

import discord
from discord.ext import commands
from discord.ext.commands import bot, Context

import reminders.const as const


def get_commands_prefix(client: bot.Bot, message: discord.message.Message) -> list:
    """
    Sets prefixes used to invoke bot's commands and enables users to invoke commands
    by tagging the bot.
    """
    prefixes = ["!", "$"]
    return commands.when_mentioned_or(*prefixes)(client, message)


async def display_error(ctx: Context, embed_description: str, text: str = None) -> None:
    embed = discord.Embed(title="Error", description=embed_description, color=0xFF0000)
    await ctx.send(text, embed=embed)


async def display_notification(
    ctx: Context, embed_description: str, text: str = None
) -> None:
    embed = discord.Embed(
        title="Notification", description=embed_description, color=0x0000FF
    )
    await ctx.send(text, embed=embed)


async def display_error_on_channel(
    channel: discord.channel.TextChannel, error_msg: str, text: str = None
) -> None:
    embed = discord.Embed(title="Error", description=error_msg, color=0xFF0000)
    await channel.send(text, embed=embed)


def utc_to_local(utc_date: dt.datetime) -> dt.datetime:
    """
    Converts datetime object with UTC timezone set to LOCAL_TIMEZONE
    timezone (MongoDB converts to UTC time automatically).
    Example:
    20:00 UTC datetime -> 22:00 Europe/Warsaw datetime.
    """
    return utc_date.replace(tzinfo=timezone.utc).astimezone(tz=const.LOCAL_TIMEZONE)


def validate_reminder_friendly_id(
    supposed_friendly_reminder_id: str,
) -> str:
    """
    Checks whether supposed reminder's friendly ID is correct.
    Returns "Success" if the check succeeded. Returns error message otherwise.
    """
    if len(supposed_friendly_reminder_id.split()) != 1:
        return "Give me a single ID!"

    if len(supposed_friendly_reminder_id) > 35:
        return "Wow, that's a long ID! Too long for sure!"
    return "Success"


def convert_to_milliseconds(current_datetime: dt.datetime) -> int:
    current_milliseconds = int(f"{current_datetime.microsecond:0<4}")
    milliseconds_stamp = sum(
        [
            int(str(current_datetime.year)[-1:]) * 365 * 31 * 24 * 60 * 60 * 1000,
            current_datetime.month * 31 * 24 * 60 * 60 * 1000,
            current_datetime.day * 24 * 60 * 60 * 1000,
            current_datetime.hour * 60 * 60 * 1000,
            current_datetime.minute * 60 * 1000,
            current_datetime.second * 1000,
            current_milliseconds,
        ]
    )
    return milliseconds_stamp
