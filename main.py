import asyncio

import discord
from discord.ext import commands

import global_const
from keep_alive import keep_alive
from reminders.reminders_bot import check_reminders


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents: discord.Intents = discord.Intents.all()
        intents.message_content = True
        intents.presences = False
        intents.members = False
        super().__init__(command_prefix="!", case_insensitive=True, intents=intents)

    async def setup_hook(self) -> None:
        await self.load_extension("reminders.reminders_bot")
        await self.load_extension("base.base")

    async def on_ready(self) -> None:
        """"""
        print("Bot is online.")
        self.loop.create_task(check_reminders(self))


keep_alive()


async def main() -> None:
    async with Bot() as bot:
        await bot.start(global_const.TOKEN)

asyncio.run(main())
