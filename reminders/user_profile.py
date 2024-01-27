import bson

import reminders.const as const
from reminders.texts import Error


def update_or_create_user_profile(
    author_id: int, inserted_reminder_id: bson.objectid.ObjectId
) -> str:
    """
    If user's profile exists in REMINDERBOT_USERS_PROFILES collection, updates it
    with the freshly made reminder's ID. If the profile doesn't exist yet, creates one
    with the reminder's ID in it.
    Returns empty string if the update/insert operation succeeded. Returns error message
    otherwise.
    """
    updating_result = const.REMINDERBOT_USERS_PROFILES.update_one(
        {"_id": author_id},
        {
            "$inc": {"future_reminders_count": 1},
            "$push": {
                "user_future_reminders": inserted_reminder_id,
                "user_all_reminders": inserted_reminder_id,
            },
        },
    )
    if updating_result.modified_count == 0:
        insertion_result = const.REMINDERBOT_USERS_PROFILES.insert_one(
            {
                "_id": author_id,
                "future_reminders_count": 1,
                "past_reminders_count": 0,
                "user_future_reminders": [inserted_reminder_id],
                "user_all_reminders": [inserted_reminder_id],
            }
        )
        if not insertion_result.inserted_id:
            return Error.TRY_AGAIN
    return ""


def update_user_profile_with_past_reminder(
    author_id: bson.int64.Int64, reminder_id: bson.objectid.ObjectId
) -> str:
    """
    Updates user's profile when a reminder is reminded. Updates reminder counts
    and pulls the reminder's ID from the user_future_reminders ID list.
    Returns empty string if the update operation succeeded. Returns error message
    otherwise.
    """
    result = const.REMINDERBOT_USERS_PROFILES.update_one(
        {"_id": author_id},
        {
            "$inc": {
                "past_reminders_count": 1,
                "future_reminders_count": -1,
            },
            "$pull": {
                "user_future_reminders": reminder_id,
            },
        },
    )
    return "" if result.modified_count else Error.CANT_REMOVE


def update_user_profile_when_canceling_reminder(
    author_id: int, reminder_to_delete_id: bson.objectid.ObjectId
) -> str:
    """
    Updates user's profile when a reminder is deleted. Decrements future reminders
    count and pulls the reminder's ID from the ID lists.
    Returns empty string if the update operation succeeded. Returns error message
    otherwise.
    """
    result = const.REMINDERBOT_USERS_PROFILES.update_one(
        {"_id": author_id},
        {
            "$inc": {"future_reminders_count": -1},
            "$pull": {
                "user_future_reminders": reminder_to_delete_id,
                "user_all_reminders": reminder_to_delete_id,
            },
        },
    )
    return "" if result.modified_count else Error.CANT_REMOVE
