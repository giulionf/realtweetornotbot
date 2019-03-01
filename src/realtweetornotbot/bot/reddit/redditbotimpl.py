import praw
import time
import traceback
from datetime import timedelta
from praw import exceptions
from realtweetornotbot.bot.reddit.config import Config
from realtweetornotbot.bot.botinterface import BotInterface
from realtweetornotbot.search.tweetfinder import TweetFinder
from realtweetornotbot.bot.urlutils import UrlUtils
from realtweetornotbot.bot.reddit.redditdb import RedditDB
from realtweetornotbot.bot.logger import Logger

ATTEMPT_TIMEOUT = 30
MAX_TIMEOUT = 11 * 60
RUN_TIMEOUT = 30 * 60

db = RedditDB()
praw_client = praw.Reddit(client_id=Config.CLIENT_ID, client_secret=Config.CLIENT_SECRET,
                          user_agent=Config.USER_AGENT, username=Config.USERNAME, password=Config.PASSWORD)


class RedditBotImpl(BotInterface):

    def fetch_new_posts(self):
        image_posts = []
        for post in praw_client.subreddit(Config.SUBREDDITS).hot(limit=Config.FETCH_COUNT):
            if RedditBotImpl.__is_valid_post(post):
                image_posts.append(post)
        db.delete_old_entries_if_db_full(len(image_posts))
        Logger.log_fetch_count(len(image_posts))

        if db.get_time_diff_since_last_summary().hour > 12:
            summary = db.get_summary()
            db.persist_summary(summary)
            RedditBotImpl.__send_summary_to_creator(summary)

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
            response = RedditBotImpl.__form_comment_response(tweets)
            RedditBotImpl.__try_repeatedly_with_timeout(lambda: RedditBotImpl.__reply_to_post(post, response))
            db.add_submission_to_seen(post.id, tweets[0].tweet.permalink)
        else:
            Logger.log_no_results(post.id, post.url)
            db.add_submission_to_seen(post.id)

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
                    Logger.log_error()
                else:
                    too_many_tries_exception = True
                    Logger.log_error_stacktrace(str(e))
                    time.sleep(ATTEMPT_TIMEOUT)

    @staticmethod
    def __reply_to_post(post, text):
        if RedditBotImpl.__is_valid_post(post):
            post.reply(text)

    @staticmethod
    def __is_valid_post(post):
        return post.url is not None and not db.is_submission_already_seen(post.id)

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

    @staticmethod
    def __send_summary_to_creator(summary):
        posts_seen = summary[0]
        tweets_found = summary[1]
        message = "New Summary:\n\nPosts Seen: {}\nTweets Found: {}".format(str(posts_seen), str(tweets_found))
        praw_client.redditor(Config.CREATOR_NAME).message("Summary", message)
