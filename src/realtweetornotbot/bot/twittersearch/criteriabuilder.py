from realtweetornotbot.bot.twittersearch.analyse import ContentProcessor, DateProcessor, ImageProcessor, UserProcessor
from realtweetornotbot.bot.twittersearch import Criteria


class CriteriaBuilder:
    """ Builder for the criteria model """

    @staticmethod
    def image_to_search_criteria_candidates(image_url):
        """ Converts an url to an image of a tweet to a list of possible search criteria """
        ocr_text = ImageProcessor.image_to_text(image_url)
        users_found = UserProcessor.find_users(ocr_text)
        dates_found = DateProcessor.find_dates(ocr_text)
        content_found = ContentProcessor.find_content(ocr_text)
        candidates = CriteriaBuilder.__create_criteria_candidates(users_found, dates_found, content_found)
        return candidates

    @staticmethod
    def __create_criteria_candidates(found_users, found_dates, content):
        candidates = []

        if len(found_users) == 0:
            return []

        if len(found_dates) == 0:
            found_dates.append("")

        for user in found_users:
            for date in found_dates:
                candidates.append(Criteria(user=user, date=date, content=content))

        return candidates
