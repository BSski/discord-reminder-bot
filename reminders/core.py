import asyncio
import datetime as dt

import discord
from discord.ext import commands
from discord.ext.commands import bot, Context
from discord.utils import escape_mentions
import pymongo

import reminders.const as const
from reminders.creating import (
    confirm_creating_reminder,
    create_reminder_to_insert,
    extract_info_from_msg,
    insert_reminder_to_database,
)
from reminders.reminding import (
    archive_reminder,
    delete_done_reminders,
    remind_user,
)
from reminders.texts import Help, Error, Info
from reminders.user_profile import (
    update_user_after_canceling,
    update_user_after_reminding,
)
from reminders.validate import (
    validate_msg,
    validate_reminder_friendly_id,
    validate_user_profile,
)
from utils.utils import (
    display_error,
    display_error_on_channel,
    display_notification,
    utc_to_local,
)


@commands.command(aliases=const.COMMANDS_ALIASES["help_reminders"])
async def help_reminders(ctx: Context) -> None:
    """Displays information about the reminder bot and its commands."""
    commands_names = {
        create_reminder: Help.CREATE_REMINDER_EXAMPLE,
        list_reminders: Help.LIST_REMINDERS_EXAMPLE,
        my_reminders: Help.MY_REMINDERS_EXAMPLE,
        show_reminder: Help.SHOW_REMINDER_EXAMPLE,
        delete_reminder: Help.DELETE_REMINDER_EXAMPLE,
    }

    embed = discord.Embed(
        title="ReminderBot",
        description=Help.HELP,
        color=0x00FF00,
    )
    for command, command_name in commands_names.items():
        embed.add_field(name=command_name, value=command.description, inline=False)
    await ctx.send(embed=embed)


@commands.command(
    aliases=const.COMMANDS_ALIASES["create_reminder"],
    description=Help.CREATE_REMINDER,
)
async def create_reminder(ctx: Context, *, msg: str = None) -> None:
    """Adds a new reminder to the database."""
    err = validate_user_profile(ctx)
    if err:
        await display_error(ctx, err)
        return

    err = validate_msg(msg)
    if err:
        await display_error(ctx, err)
        return

    msg_parts = msg.split()
    reminder_name, reminder_date, err = extract_info_from_msg(msg_parts)
    if err:
        await display_error(ctx, err)
        return

    reminder_to_insert = create_reminder_to_insert(
        ctx, reminder_name, reminder_date, msg
    )
    if err := insert_reminder_to_database(ctx.author.id, reminder_to_insert):
        await display_error(ctx, Error.INSERTION)
        return
    await confirm_creating_reminder(
        ctx, reminder_date, reminder_to_insert["friendly_id"]
    )


@commands.command(
    aliases=const.COMMANDS_ALIASES["list_reminders"],
    description=Help.LIST_REMINDERS,
)
async def list_reminders(ctx: Context) -> None:
    """Lists maximum of 8 upcoming reminders."""
    sorted_reminders = list(
        const.FUTURE_REMINDERS.find().sort("reminder_date", pymongo.ASCENDING).limit(8)
    )
    if not sorted_reminders:
        await display_notification(ctx, Info.EMPTY_LIST_NOTIFICATION)
        return

    embed = discord.Embed(
        title=":date: Upcoming reminders:",
        color=0x0000FF,
    )
    for reminder in sorted_reminders:
        remind_in = str(
            utc_to_local(reminder["reminder_date"])
            - dt.datetime.now(const.LOCAL_TIMEZONE)
        ).split(".")[0]
        embed_field_name = ":hourglass: Left: {}  |  {}:".format(
            remind_in if remind_in[0] != "-" else "0:00:00",
            utc_to_local(reminder["reminder_date"]).strftime("%d.%m.%Y %H:%M:%S"),
        )
        reminder_description = "Reminder `{}` by <@{}>: ```{}```\n".format(
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
    description=Help.MY_REMINDERS,
)
async def my_reminders(ctx: Context) -> None:
    """Lists maximum of 8 upcoming reminders that belong to the caller."""
    user_profile = const.REMINDERBOT_USERS_PROFILES.find_one({"_id": ctx.author.id})
    if not user_profile:
        await display_notification(ctx, Info.EMPTY_MY_PROFILE_NOTIFICATION)
        return

    reminder_date_sorted_user_specific_reminders = list(
        const.FUTURE_REMINDERS.find(
            {"_id": {"$in": user_profile["user_future_reminders"]}}
        )
        .sort("reminder_date", pymongo.ASCENDING)
        .limit(8)
    )
    if not reminder_date_sorted_user_specific_reminders:
        await display_notification(ctx, Info.NO_REMINDERS_NOTIFICATION)
        return

    embed = discord.Embed(
        title=f":date: Upcoming reminders by {ctx.author.nick or ctx.author.name}:",
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
        reminder_description = "Reminder `{}`\n```{}```\n".format(
            reminder["friendly_id"],
            escape_mentions(reminder["reminder_name_short"]) or "-",
        )
        embed.add_field(name=embed_field_name, value=reminder_description, inline=False)

    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await ctx.send(current_datetime, embed=embed)


@commands.command(
    aliases=const.COMMANDS_ALIASES["show_reminder"], description=Help.SHOW_REMINDER
)
async def show_reminder(ctx: Context, *, reminder_friendly_id: str = None) -> None:
    """Shows one reminder basing on a passed ID."""
    if reminder_friendly_id is None:
        await display_error(ctx, Error.NO_REMINDER_ID)
        return

    if err := validate_reminder_friendly_id(reminder_friendly_id):
        await display_error(ctx, err)
        return

    reminder = const.FUTURE_REMINDERS.find_one({"friendly_id": reminder_friendly_id})
    if reminder is None:
        await display_error(ctx, Error.NO_REMINDER_WITH_THIS_ID)
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
    reminder_description = (
        "Reminder `{}` by <@{}> ({}):\n```{}```\n*Created on {}.*".format(
            reminder["friendly_id"],
            reminder["author_id"],
            reminder["author_nick"] or reminder["author_name"],
            escape_mentions(reminder["reminder_name_full"]) or "-",
            utc_to_local(reminder["date_created"]).strftime("%d.%m.%Y %H:%M:%S"),
        )
    )
    embed.add_field(name=embed_field_name, value=reminder_description, inline=False)
    current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE).strftime(
        "%d.%m.%Y %H:%M:%S"
    )
    await ctx.send(current_datetime, embed=embed)


@commands.command(
    aliases=const.COMMANDS_ALIASES["delete_reminder"],
    description=Help.DELETE_REMINDER,
)
async def delete_reminder(ctx: Context, *, reminder_friendly_id: str = None) -> None:
    """Deletes one reminder basing on a passed ID."""
    if reminder_friendly_id is None:
        await display_error(ctx, Error.NO_REMINDER_ID_DELETE)
        return

    if err := validate_reminder_friendly_id(reminder_friendly_id):
        await display_error(ctx, err)
        return

    rmndr_to_delete = const.FUTURE_REMINDERS.find_one(
        {"friendly_id": reminder_friendly_id, "author_id": ctx.author.id}
    )
    if not rmndr_to_delete:
        await display_error(ctx, Error.NO_REMINDER_ID_DELETE)
        return

    if err := update_user_after_canceling(ctx.author.id, rmndr_to_delete["_id"]):
        await display_error(ctx, Error.TRY_AGAIN)
        return

    result = const.FUTURE_REMINDERS.delete_one(
        {"friendly_id": reminder_friendly_id, "author_id": ctx.author.id}
    )
    if result.deleted_count == 0:
        await display_error(ctx, Error.TRY_AGAIN)
        return

    reminder_description = "```{}```\n`{}`  created on  `{}`".format(
        rmndr_to_delete["reminder_name_full"] or "- ",
        rmndr_to_delete["friendly_id"],
        utc_to_local(rmndr_to_delete["date_created"]).strftime("%d.%m.%Y %H:%M:%S"),
    )
    embed = discord.Embed(
        title=":x: Deleted reminder set to {}".format(
            utc_to_local(rmndr_to_delete["reminder_date"]).strftime("%d.%m.%Y %H:%M:%S"),
        ),
        description=reminder_description,
        color=0xFFA500,
    )
    await ctx.send(embed=embed)


async def check_reminders(bot: bot.Bot) -> None:
    """Periodically checks whether there are any reminders for the current time."""
    await bot.wait_until_ready()
    channel = bot.get_channel(int(const.CHANNEL_ID))
    while not bot.is_closed():
        reminders_to_delete = []
        for reminder in const.FUTURE_REMINDERS.find():
            current_datetime = dt.datetime.now(const.LOCAL_TIMEZONE)
            reminder_datetime = utc_to_local(reminder["reminder_date"])
            if reminder_datetime > current_datetime:
                continue
            await remind_user(bot, reminder, ":exclamation: {}")

            if err := await archive_reminder(reminder):
                await display_error_on_channel(channel, err)
                continue

            if err := update_user_after_reminding(
                reminder["author_id"], reminder["_id"]
            ):
                await display_error_on_channel(channel, err)
                continue

            reminders_to_delete.append(reminder["_id"])

        if err := await delete_done_reminders(reminders_to_delete):
            print("\nCRITICAL: delete_done_reminders()\n")
            await display_error_on_channel(channel, err)
            continue
        await asyncio.sleep(const.TIME_BETWEEN_REMINDER_CHECKS)


async def setup(bot):
    bot.add_command(help_reminders)
    bot.add_command(create_reminder)
    bot.add_command(list_reminders)
    bot.add_command(my_reminders)
    bot.add_command(show_reminder)
    bot.add_command(delete_reminder)
