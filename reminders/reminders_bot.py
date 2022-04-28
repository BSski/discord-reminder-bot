import asyncio
import datetime as dt
from datetime import timezone

import discord
from discord.ext import commands
from discord.ext.commands import bot, Context
from discord.utils import escape_mentions

import reminders.const as const
from reminders.creating import (
    confirm_creating_reminder,
    create_reminder_to_insert,
    extract_info_from_msg,
    insert_reminder_to_database,
    validate_msg,
    validate_user_profile,
)
from reminders.reminding import (
    add_to_past_reminders,
    delete_done_reminders,
    remind_user,
)
from reminders.user_profile import (
    update_user_profile_when_canceling_reminder,
    update_user_profile_with_past_reminder,
)
from reminders.utils import (
    display_error,
    display_error_on_channel,
    display_notification,
    utc_to_local,
    validate_reminder_friendly_id,
)


@commands.command(aliases=const.COMMANDS_ALIASES["help_reminders"])
async def help_reminders(ctx: Context) -> None:
    """
    Displays information about the reminder bot and its commands.
    """
    commands_names = {
        create_reminder: "A) !remind me of <reminder_name> on <DD.MM.YY> <HH:MM>\nB) !remind me of <reminder_name> in <number> <unit>",
        list_reminders: "!list_reminders",
        my_reminders: "!my_reminders",
        show_reminder: "!show_reminder <ID>",
        delete_reminder: "!delete_reminder <ID>",
    }

    embed = discord.Embed(
        title="ReminderBot",
        description="I can remind you of stuff! You can mention me or use '!' prefix.\nCommands list:",
        color=0x00FF00,
    )
    for command, command_name in commands_names.items():
        embed.add_field(name=command_name, value=command.description, inline=False)
    await ctx.send(embed=embed)


@commands.command(
    aliases=const.COMMANDS_ALIASES["create_reminder"],
    description="A) Adds a reminder on <date>.\nExample: !remind me of the end of the world on 31.12.99 23:59/\nB) Adds a reminder in X time units.\nYou can use years, months, days, hours, minutes and seconds.\nExample: !remind me of cake in the oven in 3 days",
)
async def create_reminder(ctx: Context, *, msg: str = None) -> None:
    """
    Adds a new reminder to the database.
    """
    user_profile_validation_status = validate_user_profile(ctx)
    if user_profile_validation_status != "Success":
        await display_error(ctx, user_profile_validation_status)
        return

    message_validation_status = validate_msg(msg)
    if message_validation_status != "Success":
        await display_error(ctx, message_validation_status)
        return

    msg_parts = msg.split()

    reminder_name, reminder_date, extraction_status = extract_info_from_msg(
        ctx, msg_parts
    )
    if extraction_status != "Success":
        await display_error(ctx, extraction_status)
        return

    reminder_to_insert = create_reminder_to_insert(
        ctx, reminder_name, reminder_date, msg
    )
    insertion_status = insert_reminder_to_database(ctx.author.id, reminder_to_insert)
    if insertion_status != "Success":
        error_msg = "I'm sorry, something went wrong and the reminder won't work correctly. Try again!"
        await display_error(ctx, error_msg)
        return
    await confirm_creating_reminder(
        ctx, reminder_date, reminder_to_insert["friendly_id"]
    )


@commands.command(
    aliases=const.COMMANDS_ALIASES["list_reminders"],
    description="Use when you want to see everyone's reminders.",
)
async def list_reminders(ctx: Context) -> None:
    """
    Lists maximum of 10 upcoming reminders.
    """
    sorted_reminders = sorted(
        const.FUTURE_REMINDERS.find(), key=lambda reminder: reminder["reminder_date"]
    )
    if not sorted_reminders:
        notification_description = (
            "There are no reminders. Make one!\nCommand format: !remind me of X in/on Y"
        )
        await display_notification(ctx, notification_description)
        return

    embed = discord.Embed(
        title=":date: Upcoming reminders:",
        color=0x0000FF,
    )
    for reminder in sorted_reminders[-10:]:
        author = await ctx.bot.fetch_user(reminder["author_id"])
        remind_in = str(
            utc_to_local(reminder["reminder_date"])
            - dt.datetime.now(const.LOCAL_TIMEZONE)
        ).split(".")[0]
        embed_field_name = ":hourglass: Left: {}  |  {}:".format(
            remind_in if remind_in[0] != "-" else "0:00:00",
            utc_to_local(reminder["reminder_date"]).strftime("%d.%m.%Y %H:%M:%S"),
        )
        reminder_description = "Reminder ID: `{}`\n<@{}>: ```{}```\n".format(
            reminder["friendly_id"],
            reminder["author_id"],
            escape_mentions(reminder["reminder_name_short"]) or "-",
        )
        embed.add_field(name=embed_field_name, value=reminder_description, inline=False)

    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await ctx.send(current_datetime, embed=embed)


@commands.command(
    aliases=const.COMMANDS_ALIASES["my_reminders"],
    description="Use when you want to see your reminders.",
)
async def my_reminders(ctx: Context) -> None:
    """
    Lists maximum of 10 upcoming reminders that belong to the caller.
    """
    user_profile = const.REMINDERBOT_USERS_PROFILES.find_one({"_id": ctx.author.id})
    if not user_profile:
        notification_description = "You haven't made any reminders ever. Try making one!\nCommand format: !remind me of X in/on Y"
        await display_notification(ctx, notification_description)
        return

    reminder_date_sorted_user_specific_reminders = sorted(
        const.FUTURE_REMINDERS.find(
            {"_id": {"$in": user_profile["user_future_reminders"]}}
        ).limit(10),
        key=lambda reminder: reminder["reminder_date"],
    )
    if not reminder_date_sorted_user_specific_reminders:
        notification_description = "You haven't made any reminders."
        await display_notification(ctx, notification_description)
        return

    embed = discord.Embed(
        title=":date: Upcoming reminders by {}:".format(ctx.author.nick or ctx.author.name),
        color=0x0000FF,
    )
    for reminder in reminder_date_sorted_user_specific_reminders:
        remind_in = str(
            utc_to_local(reminder["reminder_date"])
            - dt.datetime.now(const.LOCAL_TIMEZONE)
        ).split(".")[0]
        embed_field_name = ":hourglass: Left: {}  |  {}:".format(
            remind_in if remind_in[0] != "-" else "0:00:00",
            utc_to_local(reminder["reminder_date"]).strftime("%d.%m.%Y %H:%M:%S"),
        )
        reminder_description = "Reminder ID: `{}`\n```{}```\n".format(
            reminder["friendly_id"],
            escape_mentions(reminder["reminder_name_short"]) or "-"
        )
        embed.add_field(name=embed_field_name, value=reminder_description, inline=False)

    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await ctx.send(current_datetime, embed=embed)


@commands.command(
    aliases=const.COMMANDS_ALIASES["show_reminder"],
    description="Use when you want to see the details of a certain reminder.\nExample: !show_reminder 32",
)
async def show_reminder(
    ctx: Context, *, supposed_reminder_friendly_id: str = None
) -> None:
    """
    Shows one reminder basing on a passed ID.
    """
    if supposed_reminder_friendly_id is None:
        error_msg = (
            "You didn't use the correct command!\nCorrect format: !show_reminder <ID>"
        )
        await display_error(ctx, error_msg)
        return

    id_validation_status = validate_reminder_friendly_id(supposed_reminder_friendly_id)
    if id_validation_status != "Success":
        await display_error(ctx, id_validation_status)
        return
    reminder_friendly_id = supposed_reminder_friendly_id

    reminder = const.FUTURE_REMINDERS.find_one({"friendly_id": reminder_friendly_id})
    if reminder is None:
        error_msg = "I can't find a reminder with this ID!"
        await display_error(ctx, error_msg)
        return

    embed = discord.Embed(
        title="Reminder by {}:".format(ctx.author.nick or ctx.author.name),
        color=0x0000FF,
    )
    remind_in = str(
        utc_to_local(reminder["reminder_date"]) - dt.datetime.now(const.LOCAL_TIMEZONE)
    ).split(".")[0]
    embed_field_name = ":hourglass: Left: {}  |  {}:".format(
        remind_in if remind_in[0] != "-" else "0:00:00",
        utc_to_local(reminder["reminder_date"]).strftime("%d.%m.%Y %H:%M:%S"),

    )
    reminder_description = "Reminder ID: `{}`\n<@{}> ({}):\n```{}```Created on: {}.".format(
        reminder["friendly_id"],
        reminder["author_id"],
        reminder["author_nick"] or reminder["author_name"],
        escape_mentions(reminder["reminder_name_full"]) or "-",
        utc_to_local(reminder["date_created"]).strftime("%d.%m.%Y %H:%M:%S"),
    )
    embed.add_field(name=embed_field_name, value=reminder_description, inline=False)
    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await ctx.send(current_datetime, embed=embed)


@commands.command(
    aliases=const.COMMANDS_ALIASES["delete_reminder"],
    description="Use when you want to delete a reminder.\nExample: !delete_reminder 15",
)
async def delete_reminder(
    ctx: Context, *, supposed_reminder_friendly_id: str = None
) -> None:
    """
    Deletes one reminder basing on a passed ID.
    """
    if supposed_reminder_friendly_id is None:
        error_msg = (
            "You didn't use the correct command!\nCorrect format: !delete_reminder <ID>"
        )
        await display_error(ctx, error_msg)
        return

    id_validation_status = validate_reminder_friendly_id(supposed_reminder_friendly_id)
    if id_validation_status != "Success":
        await display_error(ctx, id_validation_status)
        return

    reminder_friendly_id = supposed_reminder_friendly_id

    reminder_to_delete = const.FUTURE_REMINDERS.find_one(
        {"friendly_id": reminder_friendly_id, "author_id": ctx.author.id}
    )

    if not reminder_to_delete:
        error_msg = "There are no reminders of yours with this ID!"
        await display_error(ctx, error_msg)
        return

    updating_user_profile_status = update_user_profile_when_canceling_reminder(
        ctx.author.id, reminder_to_delete["_id"]
    )
    if updating_user_profile_status != "Success":
        error_msg = "Something went wrong, try again!"
        await display_error(ctx, error_msg)
        return

    reminder_deletion_status = const.FUTURE_REMINDERS.delete_one(
        {"friendly_id": reminder_friendly_id, "author_id": ctx.author.id}
    )
    if reminder_deletion_status.deleted_count == 0:
        error_msg = "Something went wrong, perhaps the reminder has not been removed!"
        await display_error(ctx, error_msg)
        return

    notification_description = "I have removed that reminder for you."
    await display_notification(ctx, notification_description)


async def check_reminders(bot: bot.Bot) -> None:
    """
    Periodically checks whether there are any reminders for the current time.
    """
    await bot.wait_until_ready()
    channel = bot.get_channel(int(const.CHANNEL_ID))
    while not bot.is_closed():
        reminders_to_delete = []
        for reminder in const.FUTURE_REMINDERS.find():
            current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE)
            reminder_datetime = utc_to_local(reminder["reminder_date"])
            if reminder_datetime > current_datetime:
                continue
            await remind_user(bot, reminder["author_id"], reminder)

            reminder_insertion_status = await add_to_past_reminders(reminder)
            if reminder_insertion_status != "Success":
                await display_error_on_channel(channel, reminder_insertion_status)
                continue

            user_profile_updating_status = update_user_profile_with_past_reminder(
                reminder["author_id"], reminder["_id"]
            )
            if user_profile_updating_status != "Success":
                await display_error_on_channel(channel, user_profile_updating_status)
                continue

            reminders_to_delete.append(reminder["_id"])

        deletion_status = await delete_done_reminders(reminders_to_delete)
        if deletion_status != "Success":
            await display_error_on_channel(channel, deletion_status)
            continue
        await asyncio.sleep(const.TIME_BETWEEN_REMINDER_CHECKS)


def setup(bot):
    bot.add_command(help_reminders)
    bot.add_command(create_reminder)
    bot.add_command(list_reminders)
    bot.add_command(my_reminders)
    bot.add_command(show_reminder)
    bot.add_command(delete_reminder)
