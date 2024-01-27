import datetime as dt
from datetime import timezone

import discord
from discord.ext import commands
from discord.ext.commands import bot, Context

import reminders.const as const
from reminders.texts import Error


def get_commands_prefix(client: bot.Bot, message: discord.message.Message) -> list:
    """
    Sets prefixes used to invoke bot's commands and enables users to invoke commands
    by tagging the bot.
    """
    prefixes = ["!", "$"]
    return commands.when_mentioned_or(*prefixes)(client, message)


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
    Returns empty string if the check succeeded. Returns error message otherwise.
    """
    if len(supposed_friendly_reminder_id.split()) != 1:
        return Error.MUST_BE_SINGLE_ID
    if len(supposed_friendly_reminder_id) > 35:
        return Error.TOO_LONG_ID
    return ""


def convert_to_milliseconds(current_datetime: dt.datetime) -> int:
    current_milliseconds = int(f"{current_datetime.microsecond:0<4}")
    return sum(
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
