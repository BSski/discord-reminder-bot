import asyncio
import datetime as dt
import discord
import pymongo
import random

from discord.ext import commands
from pymongo import MongoClient

from utils.add_reminder_utils import (
    validate_msg,
    extract_info_from_msg,
    validate_date,
    confirm_adding_reminder,
)
from utils.remind_utils import remind_user, move_to_reminded_events
from utils.other_utils import get_prefix, reply_to_greeting_with_a_chance
from keep_alive import keep_alive


SLEEP_TIME_BETWEEN_REMINDER_CHECKS = 0.3
GREETING = "elo"
CHANCE_OF_REPLYING_TO_GREETING = 4

TOKEN = os.environ['TOKEN']
MONGODB_LINK = os.environ['MONGODB_LINK']
PW = os.environ['PW']
DATABASE_NAME = os.environ['DB_NAME']
EVENTS_DONE_COLLECTION_NAME = os.environ['EVENTS_DONE_COLLECTION_NAME']
EVENTS_NOT_DONE_COLLECTION_NAME = os.environ['EVENTS_NOT_DONE_COLLECTION_NAME']

cluster = MongoClient(MONGODB_LINK.format(PW))
db = cluster[DATABASE_NAME]
events_collection = db[EVENTS_NOT_DONE_COLLECTION_NAME]
done_events_collection = db[EVENTS_DONE_COLLECTION_NAME]

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
bot.remove_command("help")


@bot.event
async def on_ready():
    print("Bot is online!")


@bot.event
async def on_message(ctx):
    """
    There is some chance that the bot will reply to a greeting with the same
    greeting. Replies X times, based on a number drawn from exponential
    distribution.
    Delete this function and related constants if you don't want this behavior.
    """
    await reply_to_greeting_with_a_chance(ctx, GREETING, CHANCE_OF_REPLYING_TO_GREETING)
    await bot.process_commands(ctx)


@bot.command()
async def help(ctx):
    """
    Displays information about the bot and its commands.
    """
    embed = discord.Embed(
        title="ReminderBot",
        description="Event reminder bot.\nMention me or use '!' prefix.\nCommands list:",
        color=0xEEE657,
    )
    embed.add_field(
        name="!remind me of <event_name> on <DD.MM.YY> <HH:MM>",
        value="Adds a reminder on <date>.\nExample: !remind me of the end of the world on 31.12.99 23:59",
        inline=False,
    )
    embed.add_field(
        name="!remind me of <event_name> in <number> <'years'/'months'/'days'/'hours'/'minutes'/'seconds'>.",
        value="Adds a reminder in X time units.\nExample: !remind me of cake in the oven in 3 days",
        inline=False,
    )
    embed.add_field(
        name="!list_events",
        value="Use when you want to see all reminders.",
        inline=False,
    )
    await ctx.send(embed=embed)


@bot.command()
async def remind(ctx, *msg_parts):
    """
    Adds a new reminder.
    """
    if validate_msg(msg_parts) == "Failed":
        await ctx.send(
            "Give me a correct command!\nFormat:\n!remind me of X in Y\n!remind me of X on DD.MM.YY HH:MM"
        )
        return

    event_name, event_date = await extract_info_from_msg(ctx, msg_parts)

    if validate_date(event_date) == "Failed":
        await ctx.send("Give me a correct input!")
        return

    data = {
        "author_id": ctx.author.id,
        "author_name": ctx.author.name,
        "author_nick": ctx.author.nick,
        "guild": ctx.guild.name,
        "event_name": event_name,
        "date_created": dt.datetime.now(),
        "event_date": event_date,
        "done": False,
        "original_message": " ".join(msg_parts),
    }

    events_collection.insert_one(data)
    await confirm_adding_reminder(ctx, event_date)


@bot.command()
async def list_events(ctx):
    """
    Lists all reminders.
    """
    events = ",\n".join(
        str(single_event) for single_event in list(events_collection.find())
    )
    await ctx.send(".\n" + events)


async def check_reminds():
    """
    Periodically checks whether there are any reminders for the current
    moment in time.
    """
    await bot.wait_until_ready()
    while not bot.is_closed():
        channel = bot.get_channel(960204135288955003)
        events_to_delete = []
        for event in events_collection.find():
            if (event["event_date"] - dt.datetime.now()).seconds < 1:
                events_collection.update_one(
                    {"_id": event["_id"]}, {"$set": {"done": True}}
                )
                events_to_delete.append(event["_id"])
                event.pop("_id")
                done_events_collection.insert_one(event)
                user_id_to_mention = event["author_id"]
                await remind_user(channel, user_id_to_mention, event)

        for id in events_to_delete:
            events_collection.delete_one({"_id": id})

        await asyncio.sleep(SLEEP_TIME_BETWEEN_REMINDER_CHECKS)


bot.loop.create_task(check_reminds())
keep_alive()
bot.run(TOKEN)
