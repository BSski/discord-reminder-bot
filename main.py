import os

import discord
from discord.ext import commands

from base.utils import reply_to_greeting_with_a_chance
import global_const
from keep_alive import keep_alive
from reminders.reminders_bot import check_reminders
from reminders.utils import get_commands_prefix

bot = commands.Bot(command_prefix=get_commands_prefix, case_insensitive=True)
bot.remove_command("help")

bot.load_extension("reminders.reminders_bot")
bot.load_extension("base.base")


@bot.event
async def on_ready() -> None:
    """
    Called when the client is done preparing the data received from Discord.
    Usually after login is successful and the Client.guilds and co. are filled up.
    """
    print("Bot is online.")
    bot.loop.create_task(check_reminders(bot))


@bot.event
async def on_message(message: discord.message.Message) -> None:
    """Called when a Message is created and sent."""
    await reply_to_greeting_with_a_chance(message, bot)
    await bot.process_commands(message)


keep_alive()

try:
    bot.run(global_const.TOKEN)
except:
    print("\nThe bot has shut down due to an error.")
