import praw
from realtweetornotbot.bot.reddit.config import Config
from realtweetornotbot.bot.botinterface import BotInterface
from realtweetornotbot.search.tweetfinder import TweetFinder
from realtweetornotbot.bot.urlutils import UrlUtils
from realtweetornotbot.bot.logger import Logger

praw_client = praw.Reddit(client_id=Config.CLIENT_ID, client_secret=Config.CLIENT_SECRET,
                          user_agent=Config.USER_AGENT, username=Config.USERNAME, password=Config.PASSWORD)


class DebugBotImpl(BotInterface):

    def fetch_new_posts(self):
        image_posts = []
        for post in praw_client.subreddit(Config.SUBREDDITS).hot(limit=Config.FETCH_COUNT):
            if DebugBotImpl.__is_valid_post(post):
                image_posts.append(post)
        Logger.log_fetch_count(len(image_posts))
        return image_posts

    def find_tweet(self, post):
        url = post.url
        if UrlUtils.is_image_submission(url):
            return TweetFinder.find_tweets(url)
        elif UrlUtils.is_imgur_submission(url):
            return TweetFinder.find_tweets(url + ".jpg")

    def handle_tweet_result(self, post, tweets):
        if tweets and len(tweets) > 0:
            Logger.log_tweet_found(post.id, post.url)
        else:
            Logger.log_no_results(post.id, post.url)

    @staticmethod
    def __is_valid_post(post):
        return post.url is not None

    @staticmethod
    def __form_comment_response(results):
        return Config.RESULT_MESSAGE.format(DebugBotImpl.__form_tweet_string(results))

    @staticmethod
    def __form_tweet_string(results):
        return "\n".join(list(map(lambda x: DebugBotImpl.__create_single_link_to_tweet(results.index(x), x), results)))

    @staticmethod
    def __create_single_link_to_tweet(index, search_result):
        return Config.SINGLE_TWEET.format(index + 1, search_result.tweet.username, search_result.score,
                                          search_result.tweet.permalink) + "\n"
