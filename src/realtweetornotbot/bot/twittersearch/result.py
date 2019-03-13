class Result:
    """ Model for a search result """

    def __init__(self, criteria, tweet, score):
        self.criteria = criteria
        self.tweet = tweet
        self.score = score
