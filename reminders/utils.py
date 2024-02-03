import datetime as dt
from datetime import timezone
import reminders.const as const


# TODO: Move to utils.utils.
def utc_to_local(utc_date: dt.datetime) -> dt.datetime:
    """
    Converts datetime object with UTC timezone set to LOCAL_TIMEZONE
    timezone (MongoDB converts to UTC time automatically).
    Example:
    20:00 UTC datetime -> 22:00 Europe/Warsaw datetime.
    """
    return utc_date.replace(tzinfo=timezone.utc).astimezone(tz=const.LOCAL_TIMEZONE)


