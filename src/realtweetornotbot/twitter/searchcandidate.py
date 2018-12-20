from datetime import timedelta


class SearchCandidate:

    def __init__(self, user, date, hashtags=None, content=""):
        self.user = user
        self.date = date
        self.hashtags = hashtags
        self.content = content

    def __repr__(self):
        return "Tweet()"

    def __str__(self):
        return "User: " + self.user + "\n" \
               + "Date: " + self.format_from_date() + "\n" \
               + "Hashtags: " + " ".join(self.hashtags) + "\n" \
               + "Content: " + self.content

    def format_from_date(self):
        if self.date:
            return (self.date - timedelta(days=1)).strftime("%Y-%m-%d")
        else:
            return ""

    def format_to_date(self):
        if self.date:
            return (self.date + timedelta(days=2)).strftime("%Y-%m-%d")
        else:
            return ""

    def format_content_to_or_query(self):
        return " OR ".join(self.content.split())
