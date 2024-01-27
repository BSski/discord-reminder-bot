# TODO: Put these in alphabetical order.
class Help:
    CREATE_REMINDER = "A) Adds a reminder on <date>.\nExample: !remind me of the end of the world on 31.12.99 23:59/\nB) Adds a reminder in X time units.\nYou can use years, months, days, hours, minutes and seconds.\nExample: !remind me of cake in the oven in 3 days"
    DELETE_REMINDER = "Use when you want to delete a reminder.\nExample: !delete_reminder 15"
    LIST_REMINDERS = "Use when you want to see everyone's reminders."
    MY_REMINDERS = "Use when you want to see your reminders."
    SHOW_REMINDER = "Use when you want to see the details of a certain reminder.\nExample: !show_reminder 32"

    HELP = "I can remind you of stuff! You can mention me or use '!' prefix.\nCommands list:"

    CREATE_REMINDER_EXAMPLE = "A) !remind me of <reminder_name> on <DD.MM.YY> <HH:MM>\nB) !remind me of <reminder_name> in <number> <unit>"
    LIST_REMINDERS_EXAMPLE = "!list_reminders"
    MY_REMINDERS_EXAMPLE = "!my_reminders"
    SHOW_REMINDER_EXAMPLE = "!show_reminder <id>"
    DELETE_REMINDER_EXAMPLE = "!delete_reminder <id>"


class Error:
    INSERTION = "I'm sorry, something went wrong and the reminder won't work correctly. Try again!"
    NO_REMINDER_ID_SHOW = "You didn't use the correct command!\nCorrect format: !show_reminder <ID>"
    NO_REMINDER_ID_DELETE = "You didn't use the correct command!\nCorrect format: !delete_reminder <ID>"
    NO_REMINDER_WITH_THIS_ID = "I can't find a reminder with this ID!"
    TRY_AGAIN = "Something went wrong, try again!"

    CANT_GET_USER = "Can't get info about this user from the database."
    TOO_MANY_ACTIVE_REMINDERS = "You've exceeded the limit! You can have maximum of 1000 active reminders."
    THROTTLE = "You've exceeded the limit! Maximum {} reminders created per {}!"
    INVALID_FORMAT = "You didn't use the correct command format!\nCorrect format: !remind me of X on/in Y"
    TOO_LONG_NAME = "That reminder name is too long!"
    NO_ON_IN_IN_MSG = 'You have to use "on" or "in" in the message!'
    WRONG_DATETIME_FORMAT = "Give me a correct datetime format!"
    WRONG_DATETIME_INFO = "Give me a correct datetime info!"
    CANT_BE_ONLY_ZEROS = "You can't give me zeros only!"
    CANT_REMIND_IN_PAST = "You can't create a reminder in the past!"
    TOO_BIG_NUMBER = "Wow, one of those numbers is way too big!"
    CANT_REMOVE = "Something went wrong when removing the reminder!"

class Info:
    EMPTY_LIST_NOTIFICATION = "There are no reminders. Make one!\nCommand format: !remind me of X in/on Y"
    EMPTY_MY_PROFILE_NOTIFICATION = "You haven't made any reminders ever. Try making one!\nCommand format: !remind me of X in/on Y"
    NO_REMINDERS_NOTIFICATION = "You haven't made any reminders."
    REMINDER_DELETED = "Reminder deleted!"


