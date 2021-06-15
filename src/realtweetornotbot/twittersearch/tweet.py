class Tweet:
    """ Internal Model for a tweet abstracted from the api used for searching on twitter """

    def __init__(self, criteria, api_tweet):
        self.user = criteria.user
        self.url = "https://twitter.com/r/status/{}".format(api_tweet['id'])
        self.content = api_tweet['text']
        self.id = api_tweet['id']
