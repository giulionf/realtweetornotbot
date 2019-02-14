from realtweetornotbot.analyse.dateprocessor import DateProcessor
from realtweetornotbot.analyse.userprocessor import UserProcessor
from realtweetornotbot.analyse.contentprocessor import ContentProcessor
from realtweetornotbot.search.searchcriteria import SearchCriteria


class TextProcessor:

    @staticmethod
    def text_to_search_criteria_candidates(text):
        found_users = UserProcessor.find_users(text)
        found_dates = DateProcessor.find_dates(text)
        content = ContentProcessor.find_content(text)
        candidates = TextProcessor.__create_search_criteria_candidates(found_users, found_dates, found_hashtags, content)
        return candidates

    @staticmethod
    def __create_search_criteria_candidates(found_users, found_dates, content):
        candidates = []

        if len(found_users) == 0:
            return []

        if len(found_dates) == 0:
            found_dates.append("")

        for user in found_users:
            for date in found_dates:
                candidates.append(SearchCriteria(user=user, date=date, content=content))

        return candidates
