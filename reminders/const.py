import os

from hashids import Hashids

from global_const import (
    CHANCE_OF_REPLYING_TO_GREETING,
    CHANNEL_ID,
    DB,
    GREETING,
    LOCAL_TIMEZONE,
)

PAST_REMINDERS_COLLECTION_NAME = os.environ["PAST_REMINDERS_COLLECTION_NAME"]
FUTURE_REMINDERS_COLLECTION_NAME = os.environ["FUTURE_REMINDERS_COLLECTION_NAME"]
REMINDERBOT_USERS_PROFILES_COLLECTION_NAME = os.environ[
    "REMINDERBOT_USERS_PROFILES_COLLECTION_NAME"
]

FUTURE_REMINDERS = DB[FUTURE_REMINDERS_COLLECTION_NAME]
PAST_REMINDERS = DB[PAST_REMINDERS_COLLECTION_NAME]
REMINDERBOT_USERS_PROFILES = DB[REMINDERBOT_USERS_PROFILES_COLLECTION_NAME]

TIME_BETWEEN_REMINDER_CHECKS = 10

hashids = Hashids()

COMMANDS_ALIASES = {
    "help_reminders": (
        "reminders_help",
        "reminder_help",
        "help_reminder",
        "help_remindesr",
        "list_remidners",
        "help-reminders",
        "help_r",
    ),
    "create_reminder": (
        "remind",
        "r",
        "remidn",
        "remnid",
        "remndi",
        "redimn",
        "renimd",
        "renidm",
        "remnd",
        "remindf",
        "reminde",
        "reminds",
    ),
    "list_reminders": (
        "reminders",
        "all_reminders",
        "show_reminders",
        "reminders_list",
        "reminders_all",
        "reminders_show",
        "list_reminder",
        "reminder_list",
        "list-reminders",
    ),
    "my_reminders": (
        "reminders_my",
        "my_remindesr",
        "my-reminders",
    ),
    "show_reminder": (
        "reminder_show",
        "show-reminder",
    ),
    "delete_reminder": (
        "reminder_delete",
        "cancel_reminder",
        "reminder_cancel",
        "delete-reminder",
        "del_reminder",
        "d_reminder",
    ),
}
