from realtweetornotbot.analyse.imageprocessor import ImageProcessor
from realtweetornotbot.bot.reddit.redditbotimpl import RedditBotImpl

SLEEP_TIME = 60 * 30


def test():
    ImageProcessor.debug = True
    post = type('', (), {})()
    post.url = 'https://pics.me.me/elon-musk-elonmusk-newprofilepic-3-42-pm-7-1-19-twitter-for-iphone-39639339.png'
    bot = RedditBotImpl()
    results = bot.find_tweet(post)
    if len(results) > 0:
        for result in results:
            print_tweet(result.tweet)
    else:
        print("No tweets found")


def print_tweet(tweet):
    print("Result: Tweet by {} {}".format(tweet.username, tweet.permalink))


if __name__ == "__main__":
    test()
