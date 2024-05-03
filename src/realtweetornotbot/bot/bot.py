from threading import Lock
import time
import traceback
from typing import List, Optional
import praw
from datetime import datetime, timedelta
from realtweetornotbot.twittersearch import TweetFinder
from realtweetornotbot.utils import Logger, UrlUtils
from realtweetornotbot.bot import Config
from src.realtweetornotbot.bot.job import BaseJob, CommentJob, PostJob
from src.realtweetornotbot.twittersearch.searchresult import TweetCandidate
from realtweetornotbot.persistance.database import Database

ATTEMPT_TIMEOUT = 30
MAX_TIMEOUT = 11 * 60
RUN_TIMEOUT = 30 * 60
class Bot:

    def __init__(self) -> None:
        self._api = praw.Reddit(client_id=Config.CLIENT_ID,
                                       client_secret=Config.CLIENT_SECRET,
                                       user_agent=Config.USER_AGENT,
                                       username=Config.USERNAME,
                                       password=Config.PASSWORD)
        self.lock = Lock()
        self.db = Database()

    def fetch_jobs(self) -> List[BaseJob]:
        mentions = self.__fetch_bot_username_mentions()
        posts = self.__fetch_posts_from_featured_subs()
        all_jobs = mentions + posts
        all_jobs = self.__filter_by_age(all_jobs)
        all_jobs = self.db.filter_unique_novel_jobs(all_jobs)
        return all_jobs
    
    def find_tweets(self, job: BaseJob) -> List[TweetCandidate]:
        url = job.get_post().url

        if UrlUtils.is_image_url(url):
            criteria = TweetFinder.build_criteria_for_image(url)
        elif UrlUtils.is_imgur_url(url):
            criteria = TweetFinder.build_criteria_for_image(url)
        else:
            criteria = []

        return TweetFinder.find_tweets(criteria)
    
    def handle_results(self, job: BaseJob, candidates: List[TweetCandidate]) -> None:
        post = job.get_post()
        if len(candidates) > 0:
            response = self.__form_comment_response(candidates)
            self.__try_until_timeout(lambda: self.__reply_to_job(job, response))
            Logger.log_tweet_found(post.id, candidates[0].tweet.url)
        else:
            Logger.log_no_results(post.id, post.url)
        self.db.on_job_done(job, candidates)

    def __fetch_posts_from_featured_subs(self) -> List[PostJob]:
        posts = []
        for post in self._api.subreddit(Config.SUBREDDITS).rising(limit=Config.FETCH_COUNT):
            posts.append(PostJob(post=post))
        Logger.log_fetch_count(len(posts))
        return posts

    def __fetch_bot_username_mentions(self) -> List[CommentJob]:
        posts = []
        for comment in self._praw_client.inbox.mentions(limit=Config.SUMMON_COUNT):
            posts.append(CommentJob(comment=comment))
        Logger.log_summon_count(len(posts))
        return posts
    
    def __filter_by_age(self, jobs: List[BaseJob]) -> List[BaseJob]:
        filtered_jobs = []
        for job in jobs:
            creation_date = datetime.fromtimestamp(job.get_post().created)
            post_age = datetime.now() - creation_date
            is_recent_post = post_age > timedelta(days=Config.POST_MAX_AGE_DAYS)
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
                if not isinstance(e, praw.exceptions.APIException) or time.time() - start_time >= MAX_TIMEOUT:
                    self.__send_pm_with_error_to_creator(traceback.format_exc())
                    Logger.log_error()
                else:
                    too_many_tries_exception = True
                    Logger.log_error_stacktrace(str(e))
                    time.sleep(ATTEMPT_TIMEOUT)
                    
    def __send_pm_with_error_to_creator(self, error):
        self.lock.acquire()
        last_100_pms = self._praw_client.inbox.sent(limit=100)
        self.lock.release()
        is_old_error = any(pm.body == str(error) for pm in last_100_pms)

        if not is_old_error:
            self.lock.acquire()
            self._praw_client.redditor(Config.CREATOR_NAME).message("New error", str(error))
            self.lock.release()
    
    def __reply_to_job(self, job: BaseJob, comment: str) -> None:
        post = job.get_post()
        if self.__is_valid_post(post):
            self.lock.acquire()
            job.reply(comment)
            self.lock.release()
            
    # def send_summary_to(self, summary: str,):
    #     posts_seen = summary[0]
    #     tweets_found = summary[1]
    #     message = "New Summary:\n\nPosts Seen: {}\nTweets Found: {}".format(str(posts_seen), str(tweets_found))
    #     self.lock.acquire()
    #     self._praw_client.redditor(Config.CREATOR_NAME).message("Summary", message)
    #     self.lock.release()

    def __form_comment_response(self, results: List[TweetCandidate]):
        formatted_tweets = map(lambda r: self.__format_candidate(results.index(r), r), results)
        single_tweets_string = "\n".join(list(formatted_tweets))
        bot_response_comment = Config.RESULT_MESSAGE.format(single_tweets_string)
        return bot_response_comment

    def __format_candidate(self, index: int, candidate: TweetCandidate):
        return f"{Config.SINGLE_TWEET.format(index + 1, candidate.score, candidate.tweet.url)}\n"
