import asyncio

import discord
from discord.ext import commands

import global_const
from keep_alive import keep_alive
from reminders.core import check_reminders


class MyHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        to_remove = "You can also use `!help [category]` for more info on a category.\n\n__**​No Category**__"
        for page in self.paginator.pages:
            embed = discord.Embed(description=page.replace(to_remove, ""))
            await destination.send(embed=embed)


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.default()
        intents.message_content = True
        intents.presences = False
        intents.members = False
        super().__init__(command_prefix="!", case_insensitive=True, intents=intents)

        self.help_command = MyHelp()

    async def setup_hook(self) -> None:
        await self.load_extension("reminders.core")
        await self.load_extension("base.base")

    async def on_ready(self) -> None:
        """on_ready can be run multiple times in some cases, we need to make sure
        the check_reminders task is only started once."""
        print("Bot is online.")
        self.loop.create_task(
            check_reminders(self)
        )  # FIXME: make sure it's run only once.


async def main() -> None:
    async with Bot() as bot:
        await bot.start(global_const.TOKEN)


keep_alive()
asyncio.run(main())

# FIXME: Fix Python warnings in the project.