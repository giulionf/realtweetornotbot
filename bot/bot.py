import logging
from threading import Lock
import time
import traceback
from typing import List
import praw
from datetime import datetime, timedelta

from bot.job import BaseJob, CommentJob, PostJob
from persistance.database import Database
from twittersearch.searchresult import TweetCandidate
# from twittersearch.tweetfinder import TweetFinder
from utils.urlutils import UrlUtils

ATTEMPT_TIMEOUT = 30
MAX_TIMEOUT = 11 * 60

__RESPONSE_TEMPLATE_SINGLE = '[{}) Tweet found ({:.2f}% sure)]({})'
__RESPONSE_TEMPLATE_FULL = (
    "^^[beep-boop,](https://www.youtube.com/watch?v=dQw4w9WgXcQ) ^^I'm ^^a ^^bot\n" \
                "\n" \
                "^(**Link to tweets:**)\n" \
                "\n" \
                "{}\n" \
                "\n" \
                "&nbsp;\n" \
                "\n" \
                "____________________________________________\n" \
                "^(If I was helpful, comment **'Good Bot'** <3! |)" \
                "^[source](https://github.com/giulionf/realtweetornotbot)" \
                "^(| created by /u/NiroxGG)"
)


class Bot:

    def __init__(
        self,
        db: Database,
        api: praw.Reddit,
        subreddits: List[str],
        fetch_post_count: int = 100,
        fetch_mention_count: int = 10,
        post_max_age_days: int = 7,
    ) -> None:
        self.lock = Lock()
        self.db = db
        self.api = api
        self.subreddits = subreddits
        self.fetch_post_count = fetch_post_count
        self.fetch_mention_count = fetch_mention_count
        self.post_max_age_days = post_max_age_days

    def fetch_jobs(self) -> List[BaseJob]:
        mentions = self.__fetch_bot_username_mentions()
        posts = self.__fetch_posts_from_featured_subs()
        all_jobs = mentions + posts
        all_jobs = self.__filter_by_age(all_jobs)
        all_jobs = self.db.filter_unique_novel_jobs(all_jobs)
        return all_jobs

    def find_tweets(self, job: BaseJob) -> List[TweetCandidate]:
        url = job.get_post().url
        return []
        
        # if UrlUtils.is_image_url(url):
        #     criteria = TweetFinder.build_criteria_for_image(url)
        # elif UrlUtils.is_imgur_url(url):
        #     criteria = TweetFinder.build_criteria_for_image(url)
        # else:
        #     criteria = []

        # return TweetFinder.find_tweets(criteria)

    def handle_results(self, job: BaseJob, candidates: List[TweetCandidate]) -> None:
        post = job.get_post()
        if len(candidates) > 0:
            tweet_url = candidates[0].tweet.url
            response = self.make_response(candidates)
            self.__try_until_timeout(lambda: self.__reply_to_job(job, response))
            logging.info(
                f"Found Tweet: Post=https://www.reddit.com/{post.id} - Tweet: {tweet_url}"
            )
        else:
            logging.info(f"No Tweet: Post=https://www.reddit.com/{post.id}")

        self.db.on_job_done(job, candidates)

    def __fetch_posts_from_featured_subs(self) -> List[PostJob]:
        posts = []
        for post in self.api.subreddit(self.subreddits).rising(
            limit=self.fetch_post_count
        ):
            posts.append(PostJob(post=post))
        logging.info(f"Fetched {len(posts)} new post jobs.")
        return posts

    def __fetch_bot_username_mentions(self) -> List[CommentJob]:
        posts = []
        for comment in self.api.inbox.mentions(limit=self.fetch_mention_count):
            posts.append(CommentJob(comment=comment))
        logging.info(f"Fetched {len(posts)} new comment jobs.")
        return posts

    def __filter_by_age(self, jobs: List[BaseJob]) -> List[BaseJob]:
        filtered_jobs = []
        for job in jobs:
            creation_date = datetime.fromtimestamp(job.get_post().created)
            post_age = datetime.now() - creation_date
            is_recent_post = post_age > timedelta(days=self.post_max_age_days)
            if job.get_post().url is not None and is_recent_post:
                filtered_jobs.append(job)
        return filtered_jobs

    def __try_until_timeout(self, func):
        start_time = time.time()
        too_many_tries_exception = True
        while too_many_tries_exception:
            try:
                too_many_tries_exception = False
                func()
            except Exception as e:
                if (
                    not isinstance(e, praw.exceptions.APIException)
                    or time.time() - start_time >= MAX_TIMEOUT
                ):
                    self.__send_pm_with_error_to_creator(traceback.format_exc())
                    logging.error(f"Exception occurred: {str(e)}")
                else:
                    too_many_tries_exception = True
                    logging.error("Attempt timed out.")
                    time.sleep(ATTEMPT_TIMEOUT)

    def __send_pm_with_error_to_creator(self, error):
        self.lock.acquire()
        last_100_pms = self._praw_client.inbox.sent(limit=100)
        self.lock.release()
        is_old_error = any(pm.body == str(error) for pm in last_100_pms)

        if not is_old_error:
            self.lock.acquire()
            # self._praw_client.redditor(Config.CREATOR_NAME).message("New error", str(error))
            self.lock.release()

    def __reply_to_job(self, job: BaseJob, comment: str) -> None:
        post = job.get_post()
        if self.__is_valid_post(post):
            self.lock.acquire()
            job.reply(comment)
            self.lock.release()
            
    def make_response(job: BaseJob, results: List[TweetCandidate]) -> str:
        formatted_results = []
        for i, result in enumerate(results):
            format_single = __RESPONSE_TEMPLATE_SINGLE.format(i, result.score, result.tweet)
            formatted_results.append(format_single)
        formatted_results_str = "\n".join(formatted_results)
        formatted_message = __RESPONSE_TEMPLATE_FULL.format(formatted_results_str)
        return formatted_message

    # def send_summary_to(self, summary: str,):
    #     posts_seen = summary[0]
    #     tweets_found = summary[1]
    #     message = "New Summary:\n\nPosts Seen: {}\nTweets Found: {}".format(str(posts_seen), str(tweets_found))
    #     self.lock.acquire()
    #     self._praw_client.redditor(Config.CREATOR_NAME).message("Summary", message)
    #     self.lock.release()

