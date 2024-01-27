import random

import discord
from discord.ext.commands import bot, Context

import global_const


async def reply_to_greeting_with_a_chance(
    message: discord.message.Message, bot: bot.Bot
) -> None:
    """
    The bot will reply to a greeting with the same greeting with some chance.
    Replies X times, based on a number drawn from exponential distribution.
    Delete this function and related constants if you don't want this behavior.
    """
    if global_const.GREETING not in message.content.lower():
        return

    if message.author == bot.user:
        return

    if random.randint(0, 99) >= global_const.CHANCE_OF_REPLYING_TO_GREETING:
        return

    channel = bot.get_channel(int(global_const.CHANNEL_ID))
    number_of_repetitions = int(random.expovariate(0.9)) + 1
    for _ in range(number_of_repetitions):
        await channel.send(global_const.GREETING)


async def display_error(ctx: Context, embed_description: str, text: str = None) -> None:
    embed = discord.Embed(title="Error", description=embed_description, color=0xFF0000)
    await ctx.send(text, embed=embed)


async def display_notification(
    ctx: Context, embed_description: str, text: str = None
) -> None:
    embed = discord.Embed(
        title="Notification", description=embed_description, color=0x0000FF
    )
    await ctx.send(text, embed=embed)
