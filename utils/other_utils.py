from discord.ext import commands


def get_prefix(client, message):
    prefixes = ["!", "$"]
    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    # Do `return prefixes` if u don't want to allow mentions instead of prefix.
    return commands.when_mentioned_or(*prefixes)(client, message)


async def reply_to_greeting_with_a_chance(
    ctx, GREETING, CHANCE_OF_REPLYING_TO_GREETING
):
    if GREETING not in str(ctx.content.lower()):
        return

    if ctx.author == bot.user:
        return

    if random.randint(0, 99) >= CHANCE_OF_REPLYING:
        return

    number_of_repetitions = int(random.expovariate(1.3)) + 1
    for _ in range(number_of_repetitions):
        await ctx.send(GREETING)
