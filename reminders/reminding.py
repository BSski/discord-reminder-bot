import bson

import discord
from discord.ext.commands import bot

import reminders.const as const
from reminders.texts import Error
from utils.utils import utc_to_local


async def remind_user(bot: bot.Bot, user_id: bson.int64.Int64, reminder: dict) -> None:
    """Sends a reminder on CHANNEL_ID channel."""
    reminder_description = "```{}```\n`{}`  created on  `{}`".format(
        reminder["reminder_name_full"] or "- ",
        reminder["friendly_id"],
        utc_to_local(reminder["date_created"]).strftime("%d.%m.%Y %H:%M:%S"),
    )
    embed = discord.Embed(
        title=":exclamation: {}".format(
            utc_to_local(reminder["reminder_date"]).strftime("%d.%m.%Y %H:%M:%S"),
        ),
        description=reminder_description,
        color=0xFFA500,
    )
    channel = bot.get_channel(int(const.CHANNEL_ID))
    author_tagging_msg = f"<@{user_id}>"
    await channel.send(author_tagging_msg, embed=embed)


async def add_to_past_reminders(reminder: dict) -> str:
    """Adds reminded reminders to PAST_REMINDERS collection."""
    reminder = reminder.copy()
    reminder["done"] = True
    result = const.PAST_REMINDERS.insert_one(reminder)
    if not result.inserted_id:
        return Error.CANT_REMOVE
    return ""


async def delete_done_reminders(
    reminders_to_delete: list[bson.objectid.ObjectId],
) -> str:
    """Deletes reminded reminders from FUTURE_REMINDERS collection."""
    for reminder_id in reminders_to_delete:
        result = const.FUTURE_REMINDERS.delete_one({"_id": reminder_id})
        if not result.deleted_count:
            return Error.CANT_REMOVE
    return ""
