from realtweetornotbot.analyse.imageprocessor import ImageProcessor
from realtweetornotbot.bot.reddit.redditbotimpl import RedditBotImpl
from realtweetornotbot.bot.reddit.config import Config

SLEEP_TIME = 60 * 30


def test_find_tweet():
    ImageProcessor.debug = True
    post = type('', (), {})()
    post.url = 'https://external-preview.redd.it/2MDrrobu8umVl2O-g7QJpCtIZc-1L9aROWIyVwbeoTE.jpg?width=645&auto=' \
               'webp&s=fcc61bc07a8c77441ca67821285d1ad947b340dd'
    bot = RedditBotImpl()
    results = bot.find_tweet(post)
    if len(results) > 0:
        for result in results:
            print("Result: Tweet by {} {}".format(result.tweet.username, result.tweet.permalink))
    else:
        print("No tweets found")


def test_comment_formatting():
    comment_tweet = Config.SINGLE_TWEET.format("1", "test", "100", "http://www.google.com");
    reply = Config.RESULT_MESSAGE.format(comment_tweet)
    print(reply)


if __name__ == "__main__":
    test_comment_formatting()
