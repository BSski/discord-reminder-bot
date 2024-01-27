import discord
from discord.ext.commands import bot, Context


async def display_error(ctx: Context, embed_description: str, text: str = None) -> None:
    embed = discord.Embed(title="Error", description=embed_description, color=0xFF0000)
    await ctx.send(text, embed=embed)


async def display_error_on_channel(
    channel: discord.channel.TextChannel, error_msg: str, text: str = None
) -> None:
    embed = discord.Embed(title="Error", description=error_msg, color=0xFF0000)
    await channel.send(text, embed=embed)


async def display_notification(
    ctx: Context, embed_description: str, text: str = None
) -> None:
    embed = discord.Embed(
        title="Notification", description=embed_description, color=0x0000FF
    )
    await ctx.send(text, embed=embed)
