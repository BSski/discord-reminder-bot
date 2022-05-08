import datetime as dt
from typing import List, Optional, Tuple

from dateutil.relativedelta import relativedelta

from discord.ext.commands import Context

import reminders.const as const
from reminders.user_profile import update_or_create_user_profile
from reminders.utils import (
    convert_to_miliseconds,
    display_notification,
    utc_to_local,
)


def validate_user_profile(ctx: Context) -> str:
    """
    Checks if the user didn't surpass any reminder limit.
    Returns "Success" if the validation succeeded. Returns error message otherwise.
    """
    user_reminders_info = const.REMINDERBOT_USERS_PROFILES.find_one(
        {"_id": ctx.author.id}
    )
    if user_reminders_info:
        user_all_reminders = user_reminders_info["user_all_reminders"]
        short_cooldown_validation_status = check_if_cooldown(
            user_all_reminders,
            time_limit_object=dt.timedelta(minutes=20),
            time_limit="20 minutes",
            max_active_reminders=30,
        )
        if short_cooldown_validation_status != "Success":
            return short_cooldown_validation_status

        long_cooldown_validation_status = check_if_cooldown(
            user_all_reminders,
            time_limit_object=dt.timedelta(days=30),
            time_limit="30 days",
            max_active_reminders=1000,
        )
        if long_cooldown_validation_status != "Success":
            return long_cooldown_validation_status

        user_future_reminders = user_reminders_info["user_future_reminders"]
        if len(user_future_reminders) > 99:
            return "You've exceeded the limit! You can have maximum of 100 active reminders."
    return "Success"


def check_if_cooldown(
    user_all_reminders: list,
    time_limit_object: dt.datetime,
    time_limit: str,
    max_active_reminders: int,
) -> str:
    """
    Checks if the user didn't surpass a reminder limit.
    Returns "Success" if the check succeeded. Returns error message otherwise.
    """
    if len(user_all_reminders) >= max_active_reminders:
        x = const.PAST_REMINDERS.find_one(
            {"_id": user_all_reminders[-max_active_reminders]}
        )
        if not x:
            x = const.FUTURE_REMINDERS.find_one(
                {"_id": user_all_reminders[-max_active_reminders]}
            )
        if not x:
            return "Something went wrong, try again!"
        if (
            utc_to_local(x["date_created"])
            > dt.datetime.now(const.LOCAL_TIMEZONE) - time_limit_object
        ):
            return "You've exceeded the limit! Maximum {} reminders created per {}!".format(
                max_active_reminders, time_limit
            )
    return "Success"


def validate_msg(msg: Optional[str]) -> str:
    """
    Checks if the content of the command fits the requirements.
    Returns "Success" if the check succeeded. Returns error message otherwise.
    """
    if msg is None:
        return "You didn't use the correct command format!\nCorrect format: !remind me of X on/in Y"

    if len(msg) > 300:
        return "That reminder name is too long!"

    msg_parts = msg.split()

    if len(msg_parts) < 5:
        return "You didn't use the correct command format!\nCorrect format: !remind me of X on/in Y"

    msg_parts = tuple(map(lambda a: a.lower(), msg_parts))
    if msg_parts[0] != "me" or msg_parts[1] != "of":
        return "You didn't use the correct command format!\nCorrect format: !remind me of [...]"

    if "on" not in msg_parts and "in" not in msg_parts:
        return "You didn't use the correct command format!\nCorrect format: !remind me of X on/in Y"
    return "Success"


def extract_info_from_msg(
    ctx: Context, msg_parts: List[str]
) -> Tuple[Optional[str], Optional[dt.datetime], str]:
    """
    Extracts reminder name and reminder date from the command's message.
    """
    if "on" in msg_parts and "in" in msg_parts:
        datetime_reminder_separator_idx = msg_parts[::-1].index("on")
        timedelta_reminder_separator_idx = msg_parts[::-1].index("in")
        if datetime_reminder_separator_idx < timedelta_reminder_separator_idx:
            (
                reminder_name,
                reminder_date,
                extraction_status,
            ) = extract_info_from_msg_datetime(ctx, msg_parts)
        else:
            (
                reminder_name,
                reminder_date,
                extraction_status,
            ) = extract_info_from_msg_timedelta(ctx, msg_parts)

    elif "on" in msg_parts:
        (
            reminder_name,
            reminder_date,
            extraction_status,
        ) = extract_info_from_msg_datetime(ctx, msg_parts)

    elif "in" in msg_parts:
        (
            reminder_name,
            reminder_date,
            extraction_status,
        ) = extract_info_from_msg_timedelta(ctx, msg_parts)
    else:
        extraction_status = "You have to use \"on\" or \"in\" in the message!"

    if extraction_status != "Success":
        return None, None, extraction_status
    return reminder_name, reminder_date, "Success"


def extract_info_from_msg_datetime(
    ctx: Context, msg_parts: List[str]
) -> Tuple[Optional[str], Optional[dt.datetime], str]:
    """
    Extracts reminder name and reminder date from the message. Runs a validation check.
    "!remind me of X on Y" (datetime) version of the function.
    """
    reminder_name_parts, reminder_date_parts = separate_name_and_date(msg_parts, "on")
    reminder_name = " ".join(reminder_name_parts)

    datetime_validation_status = validate_datetime(reminder_date_parts)
    if datetime_validation_status != "Success":
        return None, None, datetime_validation_status

    reminder_date = get_timezone_aware_datetime(ctx, reminder_date_parts)
    return reminder_name, reminder_date, datetime_validation_status


def extract_info_from_msg_timedelta(
    ctx: Context, msg_parts: List[str]
) -> Tuple[Optional[str], Optional[dt.datetime], str]:
    """
    Extracts reminder name and reminder date from the message. Runs a validation check.
    "!remind me of X in Y" (timedelta) version of the function.
    """
    reminder_name_parts, reminder_date_parts = separate_name_and_date(msg_parts, "in")
    reminder_name = " ".join(reminder_name_parts)

    if reminder_date_parts:
        reminder_date_parts = [elem for elem in reminder_date_parts if elem != "and"]

    accepted_time_units = {
        "years": ["year", "years"],
        "months": ["month", "months"],
        "days": ["day", "days"],
        "hours": ["h", "hour", "hours"],
        "minutes": ["m", "min", "mins", "minute", "minutes"],
        "seconds": ["s", "sec", "secs", "second", "seconds"],
    }

    timedelta_validation_status = validate_timedelta(
        reminder_date_parts, accepted_time_units
    )
    if timedelta_validation_status != "Success":
        return None, None, timedelta_validation_status

    reminder_date = get_timezone_aware_datetime_with_timedelta(
        ctx, reminder_date_parts, accepted_time_units
    )
    return reminder_name, reminder_date, timedelta_validation_status


def separate_name_and_date(
    msg_parts: List[str], separator_word: str
) -> Tuple[List[str], List[str]]:
    """
    Divides the command's message into reminder name parts and reminder date parts.
    """
    separator_word_idx = msg_parts[::-1].index(separator_word)
    reminder_name_parts = msg_parts[2 : -separator_word_idx - 1]
    reminder_date_parts = msg_parts[-separator_word_idx:]
    return reminder_name_parts, reminder_date_parts


def validate_datetime(reminder_date_parts: List[str]) -> str:
    """
    Checks if the datetime is correct.
    Returns "Success" if the validation succeeded. Returns error message otherwise.
    """
    reminder_date_str = " ".join(reminder_date_parts)
    try:
        reminder_date = dt.datetime.strptime(reminder_date_str, "%d.%m.%y %H:%M")
    except ValueError:
        return "Give me a correct datetime format!"

    reminder_date = const.LOCAL_TIMEZONE.localize(reminder_date)
    current_date = dt.datetime.now(const.LOCAL_TIMEZONE)

    if reminder_date < current_date:
        return "You can't create a reminder in the past!"
    return "Success"


def validate_timedelta(
    reminder_date_parts: List[str], accepted_time_units: dict
) -> str:
    """
    Checks if the timedelta information is correct.
    Returns "Success" if the validation succeeded. Returns error message otherwise.
    """
    if not reminder_date_parts:
        return "Give me correct datetime info!"

    accepted_time_units_values_flat = {
        item for sublist in accepted_time_units.values() for item in sublist
    }

    if all(
        msg_word not in accepted_time_units_values_flat
        for msg_word in reminder_date_parts
    ):
        return "Give me correct datetime info!"

    if any(
        not isinstance(elem, str) and elem not in accepted_time_units_values_flat
        if idx % 2 == 1
        else not elem.isdecimal()
        for idx, elem in enumerate(reminder_date_parts)
    ):
        return "Give me correct datetime info!"

    if all(
        int(elem) == 0 for idx, elem in enumerate(reminder_date_parts) if idx % 2 == 0
    ):
        return "You can't give me zeros only!"

    if any(
        int(elem) > 500000000 for idx, elem in enumerate(reminder_date_parts) if idx % 2 == 0
    ):
        return "Wow, one of those numbers is way too big!"
    return "Success"


def get_timezone_aware_datetime(
    ctx: Context, reminder_date_parts: List[str]
) -> dt.datetime:
    """
    Returns localized (timezone aware) future datetime of a reminder.
    """
    reminder_date_str = " ".join(reminder_date_parts)
    reminder_date = dt.datetime.strptime(reminder_date_str, "%d.%m.%y %H:%M")
    reminder_date = const.LOCAL_TIMEZONE.localize(reminder_date)
    return reminder_date


def get_timezone_aware_datetime_with_timedelta(
    ctx: Context, reminder_date_parts: List[str], accepted_time_units: dict
) -> dt.datetime:
    """
    Adds timedelta (relativedelta) to current datetime and returns timezone aware
    reminder's future datetime.
    """
    timedelta_units = dict()

    previous_item = "0"
    for item in reminder_date_parts[::-1]:
        if not previous_item.isdecimal():
            timedelta_units[previous_item] = timedelta_units.get(
                previous_item, 0
            ) + int(item)
        previous_item = item

    relative_delta = relativedelta(
        years=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["years"]),
        months=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["months"]),
        days=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["days"]),
        hours=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["hours"]),
        minutes=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["minutes"]),
        seconds=+sum(timedelta_units.get(x, 0) for x in accepted_time_units["seconds"]),
    )
    relative_delta.years = min(relative_delta.years, 20)
    reminder_date = dt.datetime.now(const.LOCAL_TIMEZONE) + relative_delta
    return reminder_date


def create_reminder_to_insert(
    ctx: Context, reminder_name: str, reminder_date: dt.datetime, user_msg: str
) -> dict:
    """
    Constructs a dictionary containing all information about a reminder.
    """
    reminder_name_short = (
        f"{reminder_name[:50]} [...]" if len(reminder_name) > 50 else reminder_name
    )
    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE)
    hash_id = const.hashids.encode(convert_to_miliseconds(current_datetime))
    data = {
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
    return data


def insert_reminder_to_database(author_id: int, data: dict) -> str:
    """
    Inserts a new reminder to the FUTURE_REMINDERS collection and updates user profile.
    Returns "Success" if the insertions succeeded. Returns error message otherwise.
    """
    reminder_insertion_status = const.FUTURE_REMINDERS.insert_one(data)
    if not reminder_insertion_status.inserted_id:
        return "Something went wrong, try again!"

    user_profile_update_or_create_status = update_or_create_user_profile(
        author_id, reminder_insertion_status.inserted_id
    )
    if user_profile_update_or_create_status != "Success":
        return "Something went wrong, try again!"
    return "Success"


async def confirm_creating_reminder(
    ctx: Context, reminder_date: dt.datetime, reminder_friendly_id: str
) -> None:
    """
    Sends a message confirming creating a new reminder.
    """
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
