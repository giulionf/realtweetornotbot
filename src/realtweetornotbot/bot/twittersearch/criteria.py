from datetime import timedelta


class Criteria:
    """ Model for a twitter search process """

    def __init__(self, user, date, content=""):
        self.user = user
        self.date = date
        self.content = content

    def __repr__(self):
        return "Tweet(\nUser: {}\nDate: {}\nContent: {}\n)".format(self.user, self.format_from_date(), self.content)

    def __str__(self):
        return "Tweet(\nUser: {}\nDate: {}\nContent: {}\n)".format(self.user, self.format_from_date(), self.content)

    def format_from_date(self):
        """ Returns the from-date formatted as a string for twitter conventions """
        if self.date:
            return (self.date - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            return ""

    def format_to_date(self):
        """ Returns the to-date formatted as a string for twitter conventions """
        if self.date:
            return (self.date + timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            return ""

    def format_content_to_or_query(self):
        """ Returns the content's words divided by an ' OR ' between each of the words """
        return " OR ".join(self.content.split())
