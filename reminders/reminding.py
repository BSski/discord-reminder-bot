import bson
from typing import List

import discord
from discord.ext.commands import bot

import reminders.const as const
from reminders.utils import utc_to_local


async def remind_user(bot: bot.Bot, user_id: bson.int64.Int64, reminder: dict) -> None:
    """Sends a reminder on CHANNEL_ID channel."""
    reminder_description = "**{}**:\nReminder ID: `{}`\n```{}```".format(
        utc_to_local(reminder["reminder_date"]).strftime("%d.%m.%Y %H:%M:%S"),
        reminder["friendly_id"],
        reminder["reminder_name_full"] or "- ",
    )
    embed = discord.Embed(
        title=":exclamation: Reminder", description=reminder_description, color=0xFFA500
    )
    channel = bot.get_channel(int(const.CHANNEL_ID))
    author_tagging_msg = f'<@{user_id}>'
    await channel.send(author_tagging_msg, embed=embed)


async def add_to_past_reminders(reminder: dict) -> str:
    """Adds reminded reminders to PAST_REMINDERS collection."""
    reminder = reminder.copy()
    reminder["done"] = True
    reminder_insertion_status = const.PAST_REMINDERS.insert_one(reminder)
    if not reminder_insertion_status.inserted_id:
        return "Something went wrong when removing the reminder!"
    return "Success"


async def delete_done_reminders(
    reminders_to_delete: List[bson.objectid.ObjectId],
) -> str:
    """Deletes reminded reminders from FUTURE_REMINDERS collection."""
    for reminder_id in reminders_to_delete:
        deletion_status = const.FUTURE_REMINDERS.delete_one({"_id": reminder_id})
        if not deletion_status.deleted_count:
            return "Something went wrong when removing a reminder!"
    return "Success"
