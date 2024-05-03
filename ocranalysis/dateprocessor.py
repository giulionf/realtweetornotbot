import re
from datetime import datetime


class DateProcessor:
    """ Helper class for extracting dates out of OCR-read text """

    DATE_REGEX_1 = r"\d{1,2}\s?[A-Za-z]{3}\s?\d{4}"             # 02 Feb 2018,   2 Feb 2018
    DATE_REGEX_2 = r"\d{1,2}\s?[A-Za-z]{3}\s?\d{2}"             # 02 Feb 18,     2 Feb 18
    DATE_REGEX_3 = r"\d{1,2}\/\d{1,2}\/\d{2}"                   # 02/02/18,      2/2/18
    DATE_REGEX_4 = r"\d{1,2}\/\d{1,2}\/\d{2}(\D|\Z)"            # 02/02/2018,    2/2/2018
    DATE_REGEX_5 = r"[A-Za-z]{3}\s?\d{1,2},\s?\d{4}"            # Feb 02, 2018,   Feb 2, 2018

    @staticmethod
    def find_dates(text):
        """ Returns the tweet's content within the total OCR text as string"""
        dates = []
        dates.extend(DateProcessor.__find_dates(text, DateProcessor.DATE_REGEX_1, "%d %b %Y"))
        if len(dates) == 0:
            dates.extend(DateProcessor.__find_dates(text, DateProcessor.DATE_REGEX_2, "%d %b %y"))
        dates.extend(DateProcessor.__find_dates(text, DateProcessor.DATE_REGEX_3, "%m/%d/%y"))
        dates.extend(DateProcessor.__find_dates(text, DateProcessor.DATE_REGEX_3, "%d/%m/%y"))
        dates.extend(DateProcessor.__find_dates(text, DateProcessor.DATE_REGEX_4, "%m/%d/%Y"))
        dates.extend(DateProcessor.__find_dates(text, DateProcessor.DATE_REGEX_4, "%d/%m/%Y"))
        dates.extend(DateProcessor.__find_dates(text, DateProcessor.DATE_REGEX_5, "%b %d, %Y"))
        dates = list(set(dates))
        return dates

    @staticmethod
    def __find_dates(text, date_regex, datetime_format):
        date_matches = re.findall(date_regex, text)
        datetime_objects = list(map(lambda d: DateProcessor.__format_date(d, datetime_format), date_matches))
        return datetime_objects

    @staticmethod
    def __format_date(date, format_string):
        try:
            return datetime.strptime(date, format_string)
        except ValueError:
            return ""
