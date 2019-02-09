import re
from datetime import datetime
from realtweetornotbot.twitter.searchcandidate import SearchCandidate

username_regex = r"@[A-Za-z0-9_]{4,15}"
date_regex = r"\d{1,2}\s?[A-Za-z]{3}\s?\d{4}"
date_regex2 = r"\d{1,2}\s?[A-Za-z]{3}\s?\d{2}"
date_regex3 = r"\d{1,2}\/\d{1,2}\/\d{1,2}"
hashtag_regex = r"#[A-Za-z0-9]*"
content_regex = r"[^a-zA-Z0-9]"


class TextProcessor:

    @staticmethod
    def find_candidates(text):
        found_users = TextProcessor.__find_users(text)
        found_dates = TextProcessor.__find_dates(text)
        found_hashtags = TextProcessor.__find_hashtags(text)
        content = TextProcessor.__find_content(text)
        candidates = TextProcessor.__create_candidates(found_users, found_dates, found_hashtags, content)
        return candidates

    @staticmethod
    def __find_users(text):
        return re.findall(username_regex, text)

    @staticmethod
    def __find_dates(text):
        date_format1 = re.findall(date_regex, text)
        date_format2 = re.findall(date_regex2, text)
        date_format3 = re.findall(date_regex3, text)
        return TextProcessor.__create_datetime_objects(date_format1, date_format2, date_format3)

    @staticmethod
    def __find_hashtags(text):
        return re.findall(hashtag_regex, text)

    @staticmethod
    def __find_content(text):
        content = re.sub('[^A-Za-z \n]+', ' ', text)                                          # Remove all special signs
        content = re.sub('\n+', ' ', content)                                                 # Replace newline by space
        content = re.sub(' +', ' ', content)                                                  # Strip multiple spaces
        content = " ".join(filter(lambda w: len(w) > 1, content.split()))                     # Remove single letters
        longest_40_words = sorted(content.split(), key=lambda x: len(x), reverse=True)[:40]
        content = " ".join(filter(lambda w: w in longest_40_words, content.split()))          # Remove short words
        return content

    @staticmethod
    def __create_candidates(found_users, found_dates, found_hashtags, content):
        candidates = []

        if len(found_users) == 0:
            return []

        if len(found_dates) == 0:
            found_dates.append("")

        for user in found_users:
            for date in found_dates:
                candidates.append(SearchCandidate(user=user, date=date, hashtags=found_hashtags, content=content))

        return candidates

    @staticmethod
    def __create_datetime_objects(date_format1, date_format2, date_format3):
        dates = list(map(lambda d: TextProcessor.__format_date(d, "%d %b %Y"), date_format1))
        dates = list(map(lambda d: TextProcessor.__format_date(d, "%d %b %y"), date_format2))
        dates.extend(map(lambda d: TextProcessor.__format_date(d, "%m/%d/%y"), date_format3))
        return dates

    @staticmethod
    def __format_date(date, format_string):
        try:
            return datetime.strptime(date, format_string)
        except ValueError:
            return ""
