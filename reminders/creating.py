import datetime as dt

from dateutil.relativedelta import relativedelta

from discord.ext.commands import Context

import reminders.const as const
from reminders.texts import Error
from reminders.user_profile import upsert_user_profile
from reminders.validate import (
    validate_datetime,
    validate_timedelta,
)
from utils.utils import display_notification


def extract_info_from_msg(
    msg_parts: list[str],
) -> tuple[str | None, dt.datetime | None, str]:
    """Extracts reminder name and reminder date from the command's message."""
    if "on" in msg_parts and "in" in msg_parts:
        datetime_reminder_separator_idx = msg_parts[::-1].index("on")
        timedelta_reminder_separator_idx = msg_parts[::-1].index("in")
        if datetime_reminder_separator_idx < timedelta_reminder_separator_idx:
            reminder_name, reminder_date, err = extract_msg_info_datetime(msg_parts)
        else:
            reminder_name, reminder_date, err = extract_msg_info_timedelta(msg_parts)
    elif "on" in msg_parts:
        reminder_name, reminder_date, err = extract_msg_info_datetime(msg_parts)
    elif "in" in msg_parts:
        reminder_name, reminder_date, err = extract_msg_info_timedelta(msg_parts)
    else:
        err = Error.NO_ON_IN_IN_MSG
    return (None, None, err) if err else (reminder_name, reminder_date, "")


def extract_msg_info_datetime(
    msg_parts: list[str],
) -> tuple[str | None, dt.datetime | None, str]:
    """
    Extracts reminder name and reminder date from the message. Runs a validation check.
    "!remind me of X on Y" (datetime) version of the function.
    """
    reminder_name_parts, reminder_date_parts = separate_name_and_date(msg_parts, "on")
    reminder_name = " ".join(reminder_name_parts)

    err = validate_datetime(reminder_date_parts)
    if err:
        return None, None, err

    reminder_date = get_timezone_aware_datetime(reminder_date_parts)
    return reminder_name, reminder_date, err


def extract_msg_info_timedelta(
    msg_parts: list[str],
) -> tuple[str | None, dt.datetime | None, str]:
    """
    Extracts reminder name and reminder date from the message. Runs a validation check.
    "!remind me of X in Y" (timedelta) version of the function.
    """
    reminder_name_parts, reminder_date_parts = separate_name_and_date(msg_parts, "in")
    reminder_name = " ".join(reminder_name_parts)

    if reminder_date_parts:
        reminder_date_parts = [elem for elem in reminder_date_parts if elem != "and"]

    accepted_time_units = {
        "years": ["y", "year", "years"],
        "months": ["mth", "month", "months"],
        "days": ["d", "day", "days"],
        "hours": ["h", "hour", "hours"],
        "minutes": ["m", "min", "mins", "minute", "minutes"],
        "seconds": ["s", "sec", "secs", "second", "seconds"],
    }

    if err := validate_timedelta(reminder_date_parts, accepted_time_units):
        return None, None, err

    reminder_date = get_timezone_aware_datetime_with_timedelta(
        reminder_date_parts, accepted_time_units
    )
    return reminder_name, reminder_date, err


def separate_name_and_date(
    msg_parts: list[str], separator_word: str
) -> tuple[list[str], list[str]]:
    """Divides the command's message into reminder name parts and reminder date parts."""
    separator_word_idx = msg_parts[::-1].index(separator_word)
    reminder_name_parts = msg_parts[: -separator_word_idx - 1]
    reminder_date_parts = msg_parts[-separator_word_idx:]
    return reminder_name_parts, reminder_date_parts


def get_timezone_aware_datetime(reminder_date_parts: list[str]) -> dt.datetime:
    """Returns localized (timezone aware) future datetime of a reminder."""
    reminder_date_str = " ".join(reminder_date_parts)
    reminder_date = dt.datetime.strptime(reminder_date_str, "%d.%m.%y %H:%M")
    reminder_date = const.LOCAL_TIMEZONE.localize(reminder_date)
    return reminder_date


def get_timezone_aware_datetime_with_timedelta(
    reminder_date_parts: list[str], accepted_time_units: dict
) -> dt.datetime:
    """
    Adds timedelta (relativedelta) to current datetime and returns timezone aware
    reminder's future datetime.
    """
    timedelta_units = {}

    previous_item = "0"
    for item in reminder_date_parts[::-1]:
        if not previous_item.isdecimal():
            timedelta_units[previous_item] = timedelta_units.get(
                previous_item, 0
            ) + int(item)
        previous_item = item

    time_offset = relativedelta(
        years=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["years"]),
        months=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["months"]),
        days=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["days"]),
        hours=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["hours"]),
        minutes=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["minutes"]),
        seconds=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["seconds"]),
    )
    time_offset.years = min(time_offset.years, 20)
    return dt.datetime.now(const.LOCAL_TIMEZONE) + time_offset


def create_reminder_to_insert(
    ctx: Context, reminder_name: str, reminder_date: dt.datetime, user_msg: str
) -> dict:
    """Constructs a dictionary containing all information about a reminder."""
    reminder_name_short = (
        f"{reminder_name[:50]} [...]" if len(reminder_name) > 50 else reminder_name
    )
    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE)

    current_milliseconds_time = int(
        current_datetime.timestamp() * 1000 + current_datetime.microsecond / 1000
    )
    hash_id = const.hashids.encode(current_milliseconds_time)
    return {
        "friendly_id": hash_id,
        "author_id": ctx.author.id,
        "author_name": ctx.author.name,
        "author_nick": ctx.author.nick,
        "guild": ctx.guild.name,
        "reminder_name_full": reminder_name,
        "reminder_name_short": reminder_name_short,
        "date_created": dt.datetime.now(const.LOCAL_TIMEZONE),
        "reminder_date": reminder_date,
        "done": False,
        "original_message": user_msg,
    }


def insert_reminder_to_database(author_id: int, data: dict) -> str:
    """
    Inserts a new reminder to the FUTURE_REMINDERS collection and updates user profile.
    Returns empty string if the insertions succeeded. Returns error message otherwise.
    """
    result = const.FUTURE_REMINDERS.insert_one(data)
    if not result.inserted_id:
        return Error.TRY_AGAIN

    if err := upsert_user_profile(author_id, result.inserted_id):
        return Error.TRY_AGAIN
    return ""


async def confirm_creating_reminder(
    ctx: Context, reminder_date: dt.datetime, reminder_friendly_id: str
) -> None:
    notification_description = (
        "I will remind you of that on **{}**, <@{}>.\nReminder's ID: `{}`".format(
            reminder_date.strftime("%d.%m.%Y %H:%M:%S"),
            ctx.author.id,
            reminder_friendly_id,
        )
    )
    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await display_notification(ctx, notification_description, text=current_datetime)
