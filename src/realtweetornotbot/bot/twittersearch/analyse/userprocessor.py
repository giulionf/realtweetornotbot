import re


class UserProcessor:
    """ Helper class for extracting user names out of OCR-read text """

    USERNAME_REGEX = r"@[A-Za-z0-9_]{4,15}"

    @staticmethod
    def find_users(text):
        """ Returns all user names found within the total OCR text as list of strings """
        return re.findall(UserProcessor.USERNAME_REGEX, text)
