import bson

import reminders.const as const


def update_or_create_user_profile(
    author_id: int, inserted_reminder_id: bson.objectid.ObjectId
) -> str:
    """
    If user's profile exists in REMINDERBOT_USERS_PROFILES collection, updates it
    with the freshly made reminder's ID. If the profile doesn't exist yet, creates one
    with the reminder's ID in it.
    Returns "Success" if the update/insert operation succeeded. Returns error message
    otherwise.
    """
    user_profile_updating_status = const.REMINDERBOT_USERS_PROFILES.update_one(
        {"_id": author_id},
        {
            "$inc": {"future_reminders_count": 1},
            "$push": {
                "user_future_reminders": inserted_reminder_id,
                "user_all_reminders": inserted_reminder_id,
            },
        },
    )
    if user_profile_updating_status.modified_count == 0:
        user_profile_insertion_status = const.REMINDERBOT_USERS_PROFILES.insert_one(
            {
                "_id": author_id,
                "future_reminders_count": 1,
                "past_reminders_count": 0,
                "user_future_reminders": [inserted_reminder_id],
                "user_all_reminders": [inserted_reminder_id],
            }
        )
        if not user_profile_insertion_status.inserted_id:
            return "Something went wrong, try again!"
    return "Success"


def update_user_profile_with_past_reminder(
    author_id: bson.int64.Int64, reminder_id: bson.objectid.ObjectId
) -> str:
    """
    Updates user's profile when a reminder is reminded. Updates reminder counts
    and pulls the reminder's ID from the user_future_reminders ID list.
    Returns "Success" if the update operation succeeded. Returns error message
    otherwise.
    """
    user_profile_updating_status = const.REMINDERBOT_USERS_PROFILES.update_one(
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
    if not user_profile_updating_status.modified_count:
        return "Something went wrong when removing the reminder!"
    return "Success"


def update_user_profile_when_canceling_reminder(
    author_id: int, reminder_to_delete_id: bson.objectid.ObjectId
) -> str:
    """
    Updates user's profile when a reminder is deleted. Decrements future reminders
    count and pulls the reminder's ID from the ID lists.
    Returns "Success" if the update operation succeeded. Returns error message
    otherwise.
    """
    user_profile_updating_status = const.REMINDERBOT_USERS_PROFILES.update_one(
        {"_id": author_id},
        {
            "$inc": {"future_reminders_count": -1},
            "$pull": {
                "user_future_reminders": reminder_to_delete_id,
                "user_all_reminders": reminder_to_delete_id,
            },
        },
    )
    if not user_profile_updating_status.modified_count:
        return "Something went wrong when canceling the reminder!"
    return "Success"
