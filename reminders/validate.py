import datetime as dt

from discord.ext.commands import Context

import reminders.const as const
from reminders.texts import Error
from utils.utils import utc_to_local


def validate_reminder_friendly_id(
    reminder_friendly_id: str,
) -> str:
    """
    Checks whether reminder's friendly ID is correct.
    Returns empty string if the check succeeded. Returns error message otherwise.
    """
    if len(reminder_friendly_id.split()) != 1:
        return Error.MUST_BE_SINGLE_ID
    if len(reminder_friendly_id) > 35:
        return Error.TOO_LONG_ID
    return ""


def validate_user_profile(ctx: Context) -> str:
    """
    Checks if the user didn't surpass any reminder limit.
    Returns empty string if the validation succeeded. Returns error message otherwise.
    """
    user_reminders_info = const.REMINDERBOT_USERS_PROFILES.find_one(
        {"_id": ctx.author.id}
    )
    if not user_reminders_info:
        return Error.CANT_GET_USER

    user_all_reminders = user_reminders_info["user_all_reminders"]
    err = check_if_cooldown(
        user_all_reminders,
        time_limit=dt.timedelta(minutes=20),  # TODO: Make it a const.
        max_active_reminders=30,
    )
    if err:
        return err

    err = check_if_cooldown(
        user_all_reminders,
        time_limit=dt.timedelta(days=30),  # TODO: Make it a const.
        max_active_reminders=1200,
    )
    if err:
        return err

    user_future_reminders = user_reminders_info["user_future_reminders"]
    if len(user_future_reminders) > 999:
        return Error.TOO_MANY_ACTIVE_REMINDERS
    return ""


def validate_msg(msg: str | None) -> str:
    """
    Checks if the content of the command fits the requirements.
    Returns empty string if the check succeeded. Returns error message otherwise.
    """
    if msg is None:
        return Error.INVALID_FORMAT

    if len(msg) > 1000:
        return Error.TOO_LONG_NAME

    msg_parts = msg.lower().split()
    if ("on" not in msg_parts) and ("in" not in msg_parts):
        return Error.INVALID_FORMAT

    return ""


def validate_datetime(reminder_date_parts: list[str]) -> str:
    """
    Checks if the datetime is correct.
    Returns empty string if the validation succeeded. Returns error message otherwise.
    """
    reminder_date_str = " ".join(reminder_date_parts)
    try:
        reminder_date = dt.datetime.strptime(reminder_date_str, "%d.%m.%y %H:%M")
    except ValueError:
        return Error.WRONG_DATETIME_FORMAT

    reminder_date = const.LOCAL_TIMEZONE.localize(reminder_date)
    current_date = dt.datetime.now(const.LOCAL_TIMEZONE)

    if reminder_date < current_date:
        return Error.CANT_REMIND_IN_PAST

    return ""


def validate_timedelta(
    reminder_date_parts: list[str], accepted_time_units: dict
) -> str:
    """
    Checks if the timedelta information is correct.
    Returns empty string if the validation succeeded. Returns error message otherwise.
    """
    if not reminder_date_parts:
        return Error.WRONG_DATETIME_INFO

    accepted_time_units_values_flat = {
        item for sublist in accepted_time_units.values() for item in sublist
    }

    if all(
        msg_word not in accepted_time_units_values_flat
        for msg_word in reminder_date_parts
    ):
        return Error.WRONG_DATETIME_INFO

    # FIXME: Make these "if any" separate funcs.
    if any(
        (
            not isinstance(elem, str) and elem not in accepted_time_units_values_flat
            if idx % 2 == 1
            else not elem.isdecimal()
        )
        for idx, elem in enumerate(reminder_date_parts)
    ):
        return Error.WRONG_DATETIME_INFO

    if all(
        int(elem) == 0 for idx, elem in enumerate(reminder_date_parts) if idx % 2 == 0
    ):
        return Error.CANT_BE_ONLY_ZEROS

    if any(
        int(elem) > 500000000
        for idx, elem in enumerate(reminder_date_parts)
        if idx % 2 == 0
    ):
        return Error.TOO_BIG_NUMBER

    return ""


def check_if_cooldown(
    user_all_reminders: list,
    time_limit: dt.timedelta,
    max_active_reminders: int,
) -> str:
    """
    Checks if the user didn't surpass a reminder limit.
    Returns empty string if the check succeeded. Returns error message otherwise.
    """
    if len(user_all_reminders) < max_active_reminders:
        return ""

    r = const.PAST_REMINDERS.find_one(
        {"_id": user_all_reminders[-max_active_reminders]}
    )
    if not r:
        r = const.FUTURE_REMINDERS.find_one(
            {"_id": user_all_reminders[-max_active_reminders]}
        )
    if not r:
        return Error.TRY_AGAIN

    max_allowed_past_datetime = dt.datetime.now(const.LOCAL_TIMEZONE) - time_limit
    if utc_to_local(r["date_created"]) > max_allowed_past_datetime:
        return Error.THROTTLE.format(max_active_reminders, time_limit)

    return ""
