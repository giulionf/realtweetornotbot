import praw
import time
import traceback
from datetime import timedelta
from praw import exceptions
from threading import Lock
from realtweetornotbot.bot import Config, Database, DebugBot
from realtweetornotbot.utils import Logger

ATTEMPT_TIMEOUT = 30
MAX_TIMEOUT = 11 * 60
RUN_TIMEOUT = 30 * 60

db = Database()
praw_lock = Lock()


class Bot(DebugBot):
    """ Bot that detects tweets in image posts, analyzes them and posts the results in the comments """

    def __init__(self):
        DebugBot.__init__(self)

    def fetch_new_posts(self):
        image_posts = super().fetch_new_posts()
        db.delete_old_entries_if_db_full(len(image_posts))
        self.__update_database_summary()
        return image_posts

    def handle_tweet_result(self, post, tweets):
        super().handle_tweet_result(post, tweets)
        if tweets and len(tweets) > 0:
            response = DebugBot._form_comment_response(tweets)
            self.__try_repeatedly_with_timeout(lambda: self.__reply_to_post(post, response))
            db.add_submission_to_seen(post.id, tweets[0].tweet.permalink)
        else:
            db.add_submission_to_seen(post.id)

    def __try_repeatedly_with_timeout(self, func):
        start_time = time.time()
        too_many_tries_exception = True
        while too_many_tries_exception:
            try:
                too_many_tries_exception = False
                func()
            except Exception as e:
                if not isinstance(e, praw.exceptions.APIException) or time.time() - start_time >= MAX_TIMEOUT:
                    self.__send_pm_with_error_to_creator(traceback.format_exc())
                    Logger.log_error()
                else:
                    too_many_tries_exception = True
                    Logger.log_error_stacktrace(str(e))
                    time.sleep(ATTEMPT_TIMEOUT)

    def __send_pm_with_error_to_creator(self, error):
        praw_lock.acquire()
        last_100_pms = self._praw_client.inbox.sent(limit=100)
        praw_lock.release()
        is_old_error = any(pm.body == str(error) for pm in last_100_pms)

        if not is_old_error:
            praw_lock.acquire()
            self._praw_client.redditor(Config.CREATOR_NAME).message("New error", str(error))
            praw_lock.release()

    def __update_database_summary(self):
        time_since_last_summary = db.get_time_diff_since_last_summary()
        Logger.log_summary_time(time_since_last_summary)
        if time_since_last_summary > timedelta(hours=Config.DATABASE_SUMMARY_INTERVAL_HOURS):
            summary = db.get_summary()
            db.delete_old_summaries_if_db_full()
            db.persist_summary(summary)
            self.__send_summary_to_creator(summary)

    def __send_summary_to_creator(self, summary):
        posts_seen = summary[0]
        tweets_found = summary[1]
        message = "New Summary:\n\nPosts Seen: {}\nTweets Found: {}".format(str(posts_seen), str(tweets_found))
        praw_lock.acquire()
        self._praw_client.redditor(Config.CREATOR_NAME).message("Summary", message)
        praw_lock.release()

    def _is_valid_post(self, post):
        return super()._is_valid_post(post) and not db.is_submission_already_seen(post.id)

    def __reply_to_post(self, post, text):
        if self._is_valid_post(post):
            praw_lock.acquire()
            post.reply(text)
            praw_lock.release()
