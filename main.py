import discord
from discord.ext import commands

import global_const
from keep_alive import keep_alive
from reminders.reminders_bot import check_reminders
from reminders.utils import get_commands_prefix

intents = discord.Intents.default()
bot = commands.Bot(command_prefix=get_commands_prefix, case_insensitive=True, intents=intents)
bot.remove_command("help")

bot.load_extension("reminders.reminders_bot")
bot.load_extension("base.base")


@bot.event
async def on_ready() -> None:
    """
    // TODO: Update this docstring after migrating to Discord.py 2.0.
    Called when the client is done preparing the data received from Discord.
    Usually after login is successful and the Client.guilds and co. are filled up.
    """
    print("Bot is online.")
    bot.loop.create_task(check_reminders(bot))


# TODO: Establish if can delete this one.
@bot.event
async def on_message(message: discord.message.Message) -> None:
    """
    // TODO: Update this docstring after migrating to Discord.py 2.0.
    Called when a Message is created and sent.
    """
    await bot.process_commands(message)


keep_alive()

try:
    bot.run(global_const.TOKEN)
except:
    print("\nThe bot has shut down due to an error.")
