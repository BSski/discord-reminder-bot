import os

from pymongo import MongoClient

import pytz


DATABASE_NAME = os.environ["DATABASE_NAME"]
MONGODB_LINK = os.environ["MONGODB_LINK"]
PW = os.environ["PW"]

TOKEN = os.environ["TOKEN"]
CHANNEL_ID = os.environ["CHANNEL_ID"]
LOCAL_TIMEZONE = pytz.timezone(os.environ["LOCAL_TIMEZONE"])

CLUSTER = MongoClient(MONGODB_LINK.format(PW))
DB = CLUSTER[DATABASE_NAME]

GREETING = "elo"
CHANCE_OF_REPLYING_TO_GREETING = 4

COMMANDS_ALIASES = {
    "shutdown": (),
    "say_datetime": (
        "datetime",
        "date",
        "time",
        "show_datetime",
        "say_date",
        "say_time",
        "show_date",
        "show_time",
        "timedate",
        "say_timedate",
    ),
    "display_help": (
        "help",
        "hlep",
        "hepl",
        "elhp",
        "how",
        "bot",
        "hi",
        "start",
        "manual",
        "instruction",
        "instructions",
    ),
}
