import praw
import time
import traceback
from praw import exceptions
from bot.reddit.config import Config
from realtweetornotbot.bot.botinterface import BotInterface
from realtweetornotbot.search.tweetfinder import TweetFinder
from bot.urlutils import UrlUtils

ATTEMPT_TIMEOUT = 30
MAX_TIMEOUT = 11 * 60
RUN_TIMEOUT = 30 * 60
POST_FETCH_COUNT = 100

praw_client = praw.Reddit(client_id=Config.CLIENT_ID, client_secret=Config.CLIENT_SECRET,
                          user_agent=Config.USER_AGENT, username=Config.USERNAME, password=Config.PASSWORD)


class RedditBotImpl(BotInterface):

    def fetch_new_posts(self):
        image_posts = []
        for post in praw_client.subreddit(Config.SUBREDDITS).hot(limit=POST_FETCH_COUNT):
            if RedditBotImpl.__is_valid_post(post):
                image_posts.append(post)
        print("Fetched {} new submissions".format(len(image_posts)))
        return image_posts

    def get_image_url_from_post(self, post):
        return post.url

    def find_tweet(self, post):
        url = self.get_image_url_from_post(post)
        print("Searching for tweets in: {}".format(url))
        if UrlUtils.is_image_submission(url):
            return TweetFinder.find_tweets(url)
        elif UrlUtils.is_imgur_submission(url):
            return TweetFinder.find_tweets(url + ".jpg")

    def handle_tweet_result(self, post, tweets):
        if tweets and len(tweets) > 0:
            print("{} tweets - Replying to {} in {}".format(len(tweets), post.author.name, post.subreddit.display_name))
            response = RedditBotImpl.__form_comment_response(tweets)
            RedditBotImpl.__try_repeatedly_with_timeout(lambda: RedditBotImpl.__reply_to_post(post, response))
        else:
            print("No results for submission by {} in {}".format(post.author.name, post.subreddit.display_name))
        post.save()

    @staticmethod
    def __try_repeatedly_with_timeout(func):
        start_time = time.time()
        too_many_tries_exception = True
        while too_many_tries_exception:
            try:
                too_many_tries_exception = False
                func()
            except Exception as e:
                if not isinstance(e, praw.exceptions.APIException) or time.time() - start_time >= MAX_TIMEOUT:
                    RedditBotImpl.__send_pm_with_error_to_creator(traceback.format_exc())
                    print("Error occured")
                else:
                    too_many_tries_exception = True
                    print("PRAW API Exception!: {}".format(str(e)))
                    time.sleep(ATTEMPT_TIMEOUT)

    @staticmethod
    def __reply_to_post(post, text):
        if RedditBotImpl.__is_valid_post(post):
            post.reply(text)

    @staticmethod
    def __is_valid_post(post):
        return not post.saved and post.url is not None

    @staticmethod
    def __form_comment_response(results):
        return Config.RESULT_MESSAGE.format(RedditBotImpl.__form_tweet_string(results))

    @staticmethod
    def __form_tweet_string(results):
        return "\n".join(list(map(lambda x: RedditBotImpl.__create_single_link_to_tweet(results.index(x), x), results)))

    @staticmethod
    def __create_single_link_to_tweet(index, search_result):
        return Config.SINGLE_TWEET.format(index + 1, search_result.tweet.username, search_result.score,
                                          search_result.tweet.permalink) + "\n"

    @staticmethod
    def __send_pm_with_error_to_creator(error):
        last_100_pms = praw_client.inbox.sent(limit=100)
        is_old_error = any(pm.body == str(error) for pm in last_100_pms)

        if not is_old_error:
            praw_client.redditor(Config.CREATOR_NAME).message("New error", str(error))
