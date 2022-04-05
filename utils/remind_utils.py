async def remind_user(channel, user_id, event):
    await channel.send(
        "<@{}>\n{}: {}!".format(
            user_id,
            event["event_date"].strftime("%d.%m.%Y %H:%M:%S"),
            event["event_name"],
        )
    )


async def move_to_reminded_events():
    """
    #TODO!
    """
    await ctx.send("Reminder")
