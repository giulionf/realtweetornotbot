import re
from datetime import datetime
from realtweetornotbot.comment.commandparameters import CommandParameters


COMMAND_DATE_REGEX = r'date="?\'?\d{4}-\d{1,2}-\d{1,2}"?\'?'
COMMAND_USER_REGEX = r'username="?\'?@?[A-Za-z0-9_]{4,15}"?\'?'


class CommandUtils:

    @staticmethod
    def get_comment_parameters(comment_text):
        user = CommandUtils.__get_user(comment_text)
        date = CommandUtils.__get_date(comment_text)
        return CommandParameters(user, date)

    @staticmethod
    def __get_user(comment_text):
        users = re.findall(COMMAND_USER_REGEX, comment_text)
        user = users[0] if len(users) > 0 and users[0] else ""
        user = re.sub('username=|["@\']', "", user)
        return user

    @staticmethod
    def __get_date(comment_text):
        dates = re.findall(COMMAND_DATE_REGEX, comment_text)
        date = dates[0] if len(dates) > 0 and dates[0] else ""
        date = re.sub('date=|["\']', "", date)                       # at this point it can only be in YYYY-MM-DD format

        try:
            return datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return ""
