import re
from datetime import datetime
from realtweetornotbot.twitter.searchcandidate import SearchCandidate

username_regex = r"@[A-Za-z0-9_]{4,15}"
date_regex = r"\d{1,2}\s?[A-Za-z]{3}\s?\d{4}"
old_date_regex = r"\d{1,2}\/\d{1,2}\/\d{1,2}"
hashtag_regex = r"#[A-Za-z0-9]*"
content_regex = r"[^a-zA-Z0-9]"


class TextProcessor:

    @staticmethod
    def find_candidates(text, parameters):
        found_users = TextProcessor.__find_users(text) if not parameters.user else [parameters.user]
        found_dates = TextProcessor.__find_dates(text) if not parameters.date else [parameters.date]
        found_hashtags = TextProcessor.__find_hashtags(text)
        content = TextProcessor.__find_content(text)
        candidates = TextProcessor.__create_candidates(found_users, found_dates, found_hashtags, content)
        return candidates

    @staticmethod
    def __find_users(text):
        return re.findall(username_regex, text)

    @staticmethod
    def __find_dates(text):
        new_dates = re.findall(date_regex, text)
        old_dates = re.findall(old_date_regex, text)
        return TextProcessor.__create_datetime_objects(new_dates, old_dates)

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
    def __create_datetime_objects(found_dates, found_old_dates):
        dates = list(map(lambda d: TextProcessor.__format_date(d, "%d %b %Y"), found_dates))
        dates.extend(map(lambda d: TextProcessor.__format_date(d, "%m/%d/%y"), found_old_dates))
        return dates

    @staticmethod
    def __format_date(date, format_string):
        try:
            return datetime.strptime(date, format_string)
        except ValueError:
            return ""
