import praw
from datetime import datetime, timedelta
from realtweetornotbot.twittersearch import TweetFinder
from realtweetornotbot.utils import Logger, UrlUtils
from realtweetornotbot.bot import Config
from realtweetornotbot.multithreading.job import Job


class DebugBot:
    """ Basic Bot Implementation usable for debugging """

    def __init__(self):
        self._praw_client = praw.Reddit(client_id=Config.CLIENT_ID,
                                        client_secret=Config.CLIENT_SECRET,
                                        user_agent=Config.USER_AGENT,
                                        username=Config.USERNAME,
                                        password=Config.PASSWORD)

    def fetch_new_jobs(self):
        """ Fetches new jobs to work off. Jobs might be of type:
            - comment (a summon of another user by comment)
            - post (an image post)

        Returns
        -------
        list
            a list of praw.submissions to work off
        """
        posts_from_mentions = self.__fetch_new_username_mentions()
        posts_from_subs = self.__fetch_new_posts_from_featured_subs()
        posts = list(set().union(posts_from_mentions, posts_from_subs))
        return posts

    def __fetch_new_posts_from_featured_subs(self):
        image_posts = []
        for post in self._praw_client.subreddit(Config.SUBREDDITS).rising(limit=Config.FETCH_COUNT):
            if self._is_valid_post(post):
                image_posts.append(Job(Job.JobType.POST, post))
        Logger.log_fetch_count(len(image_posts))
        return image_posts

    def __fetch_new_username_mentions(self):
        image_posts = []
        for comment in self._praw_client.inbox.mentions(limit=Config.SUMMON_COUNT):
            if self._is_valid_post(comment.submission):
                image_posts.append(Job(Job.JobType.COMMENT, comment))
        Logger.log_summon_count(len(image_posts))
        return image_posts

    def find_tweet(self, job):
        """ Finds a tweet for a given job

        Parameters
        ----------
        job : Job

        Returns
        -------
        list
            a list of twittersearch.result for the job
        """
        url = job.get_post().url

        if UrlUtils.is_image_url(url):
            criteria = TweetFinder.build_criteria_for_image(url)
        elif UrlUtils.is_imgur_url(url):
            criteria = TweetFinder.build_criteria_for_image(url)
        else:
            criteria = []

        return TweetFinder.find_tweets(criteria)

    def handle_tweet_result(self, job, search_results):
        """ Implements the actions made on new results on a job

        Parameters
        ----------
        job : Job

        search_results : list
            results for the given post
        """
        post = job.get_post()
        if search_results and len(search_results) > 0:
            Logger.log_tweet_found(post.id, search_results[0].tweet.url)
        else:
            Logger.log_no_results(post.id, post.url)

    def _is_valid_post(self, post):
        creation_date = datetime.fromtimestamp(post.created)
        post_age = datetime.now() - creation_date
        return post.url is not None and post_age <= timedelta(days=Config.POST_MAX_AGE_DAYS)

    @staticmethod
    def _form_comment_response(results):
        return Config.RESULT_MESSAGE.format(DebugBot._form_tweet_string(results))

    @staticmethod
    def _form_tweet_string(results):
        return "\n".join(list(map(lambda x: DebugBot._create_single_link_to_tweet(results.index(x), x), results)))

    @staticmethod
    def _create_single_link_to_tweet(index, search_result):
        return Config.SINGLE_TWEET.format(index + 1, search_result.score, search_result.tweet.url) + "\n"
