from realtweetornotbot.result.error import SearchError

LOW_MATCH_PERCENT = 70


class SearchResult:

    def __init__(self, searchcandidate, tweet, score):
        self.searchcandidate = searchcandidate
        self.tweet = tweet
        self.score = score
        self.errors = []

        if not searchcandidate.date:
            self.errors.append(SearchError.NO_DATE)

        if not searchcandidate.user:
            self.errors.append(SearchError.NO_USER)

        if len(self.errors) == 0 and self.score < LOW_MATCH_PERCENT:
            self.errors.append(SearchError.LOW_MATCH)
