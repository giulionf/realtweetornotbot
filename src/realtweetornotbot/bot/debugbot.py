from typing import List, Optional
import praw
from datetime import datetime, timedelta
from realtweetornotbot.twittersearch import TweetFinder
from realtweetornotbot.utils import Logger, UrlUtils
from realtweetornotbot.bot import Config
from src.realtweetornotbot.bot.job import BaseJob, CommentJob, PostJob
from src.realtweetornotbot.twittersearch.searchresult import SearchResult, TweetCandidate


class DebugBot:

    def __init__(self) -> None:
        self._api = praw.Reddit(client_id=Config.CLIENT_ID,
                                       client_secret=Config.CLIENT_SECRET,
                                       user_agent=Config.USER_AGENT,
                                       username=Config.USERNAME,
                                       password=Config.PASSWORD)

    def fetch_jobs(self) -> List[BaseJob]:
        mentions = self.__fetch_bot_username_mentions()
        posts = self.__fetch_posts_from_featured_subs()
        all_posts = mentions + posts
        return all_posts

    def __fetch_posts_from_featured_subs(self) -> List[PostJob]:
        posts = []
        for post in self._api.subreddit(Config.SUBREDDITS).rising(limit=Config.FETCH_COUNT):
            if self.__is_valid_post(post):
                posts.append(PostJob(post=post))
        Logger.log_fetch_count(len(posts))
        return posts

    def __fetch_bot_username_mentions(self) -> List[CommentJob]:
        posts = []
        for comment in self._praw_client.inbox.mentions(limit=Config.SUMMON_COUNT):
            if self.__is_valid_post(comment.submission):
                posts.append(CommentJob(comment=comment))
        Logger.log_summon_count(len(posts))
        return posts

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
            Logger.log_tweet_found(post.id, candidates[0].tweet.url)
        else:
            Logger.log_no_results(post.id, post.url)

    def __is_valid_post(self, post):
        creation_date = datetime.fromtimestamp(post.created)
        post_age = datetime.now() - creation_date
        return post.url is not None and post_age <= timedelta(days=Config.POST_MAX_AGE_DAYS)

    @staticmethod
    def __form_comment_response(results: List[TweetCandidate]):
        formatted_tweets = map(lambda r: DebugBot.__format_candidate(results.index(r), r), results)
        single_tweets_string = "\n".join(list(formatted_tweets))
        bot_response_comment = Config.RESULT_MESSAGE.format(single_tweets_string)
        return bot_response_comment

    @staticmethod
    def __format_candidate(index, candidate: TweetCandidate):
        return f"{Config.SINGLE_TWEET.format(index + 1, candidate.score, candidate.tweet.url)}\n"
