import datetime as dt


class Criteria:
    """ Model for a twitter search process """

    def __init__(self, user, date, content=""):
        self.user = user
        self.date = date
        self.content = content

    def __repr__(self):
        return "Criteria(\nUser: {}\nDate: {}\nContent: {}\n)".format(self.user, self.format_from_date(), self.content)

    def __str__(self):
        return "Criteria(\nUser: {}\nDate: {}\nContent: {}\n)".format(self.user, self.format_from_date(), self.content)

    def from_date(self):
        """ Returns the begin date of the query (detected date - 1 day of padding)"""
        return self.date - dt.timedelta(days=1) if self.date else dt.date(2006, 3, 21)

    def to_date(self):
        """ Returns the end date of the query (detected date + 2 days of padding) """
        return self.date + dt.timedelta(days=2) if self.date else dt.date.today()

    def format_from_date(self):
        """ Returns the from-date formatted as a string for twitter conventions """
        if self.date:
            return (self.from_date()).strftime("%Y-%m-%d")
        else:
            return ""

    def format_to_date(self):
        """ Returns the to-date formatted as a string for twitter conventions """
        if self.date:
            return (self.to_date()).strftime("%Y-%m-%d")
        else:
            return ""

    def format_content(self):
        """ Returns the content of the tweet seperated by 'OR' operators"""
        return " OR ".join(self.content.split())

    def to_query(self):
        """ Returns the tweets content and user in the twitter search query format """
        return "from:{} since:{} until:{} {}".format(self.user,
                                                     self.format_from_date(),
                                                     self.format_to_date(),
                                                     self.format_content())
