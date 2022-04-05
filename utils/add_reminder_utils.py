import datetime as dt

from dateutil.relativedelta import relativedelta


def validate_msg(msg_parts):
    failed_msg = "Failed"
    if len(msg_parts) < 2:
        return failed_msg

    if msg_parts[0] != "me" or msg_parts[1] != "of":
        return failed_msg

    if "on" not in msg_parts and "in" not in msg_parts:
        return failed_msg


async def extract_info_from_msg(ctx, msg_parts):
    if "on" in msg_parts and "in" in msg_parts:
        on_word_idx = msg_parts[::-1].index("on")
        in_word_idx = msg_parts[::-1].index("in")

        if on_word_idx < in_word_idx:
            event_name, event_date = await get_full_event_info_on_version(
                ctx, msg_parts
            )
        else:
            event_name, event_date = await get_full_event_info_in_version(
                ctx, msg_parts
            )

    if "on" in msg_parts and "in" not in msg_parts:
        event_name, event_date = await get_full_event_info_on_version(ctx, msg_parts)

    if "on" not in msg_parts and "in" in msg_parts:
        event_name, event_date = await get_full_event_info_in_version(ctx, msg_parts)

    return event_name, event_date


def validate_date(event_date):
    failed_msg = "Failed"
    current_date = dt.datetime.now()
    if event_date < current_date:
        return failed_msg


async def confirm_adding_reminder(ctx, event_date):
    await ctx.send(
        "Your new reminder has been added on {}, {}.".format(
            event_date.strftime("%d.%m.%Y %H:%M:%S"),
            ctx.author.nick if ctx.author.nick else ctx.author.name,
        )
    )


def get_event_name_and_date(msg_parts, separator_word):
    separator_idx = msg_parts[::-1].index(separator_word)
    event_name = msg_parts[2 : -separator_idx - 1]
    event_name = " ".join(event_name)
    event_date = msg_parts[-separator_idx:]
    return event_name, event_date


async def get_full_event_info_on_version(ctx, msg_parts):
    event_name, event_date = get_event_name_and_date(msg_parts, "on")
    event_date = " ".join(event_date)
    event_date = dt.datetime.strptime(event_date, "%d.%m.%y %H:%M")
    return event_name, event_date


async def get_full_event_info_in_version(ctx, msg_parts):
    event_name, event_date = get_event_name_and_date(msg_parts, "in")
    event_time_info = {
        "years": 0,
        "months": 0,
        "days": 0,
        "hours": 0,
        "minutes": 0,
        "seconds": 0,
    }

    previous_item = ""
    for item in event_date[::-1]:
        if previous_item in event_time_info.keys():
            try:
                event_time_info[previous_item] = abs(int(item))
            except ValueError:
                event_time_info[previous_item] = 0
                await ctx.send("Your reminder might contain mistakes.")
        previous_item = item

    event_date = dt.datetime.now() + relativedelta(
        years=+event_time_info["years"],
        months=+event_time_info["months"],
        days=+event_time_info["days"],
        hours=+event_time_info["hours"],
        minutes=+event_time_info["minutes"],
        seconds=+event_time_info["seconds"],
    )

    return event_name, event_date
