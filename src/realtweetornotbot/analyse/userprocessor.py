import re


class UserProcessor:

    USERNAME_REGEX = r"@[A-Za-z0-9_]{4,15}"   # @Username

    @staticmethod
    def find_users(text):
        return re.findall(UserProcessor.USERNAME_REGEX, text)
