import praw
from datetime import datetime, timedelta
from realtweetornotbot.bot import Config
from realtweetornotbot.bot.twittersearch import TweetFinder
from realtweetornotbot.utils import Logger, UrlUtils


class DebugBot:
    """ Basic Bot Implementation usable for debugging """

    def __init__(self):
        self._praw_client = praw.Reddit(client_id=Config.CLIENT_ID,
                                        client_secret=Config.CLIENT_SECRET,
                                        user_agent=Config.USER_AGENT,
                                        username=Config.USERNAME,
                                        password=Config.PASSWORD)

    def fetch_new_posts(self):
        """ Fetches new posts to work off

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
        for post in self._praw_client.subreddit(Config.SUBREDDITS).hot(limit=Config.FETCH_COUNT):
            if self._is_valid_post(post):
                image_posts.append(post)
        Logger.log_fetch_count(len(image_posts))
        return image_posts

    def __fetch_new_username_mentions(self):
        image_posts = []
        for comment in self._praw_client.inbox.mentions(limit=Config.SUMMON_COUNT):
            if self._is_valid_post(comment.submission):
                image_posts.append(comment.submission)
        Logger.log_summon_count(len(image_posts))
        return image_posts

    def find_tweet(self, post):
        """ Finds a tweet for a given post

        Parameters
        ----------
        post : praw.submission
            The post to find tweets in

        Returns
        -------
        list
            a list of twittersearch.result for the post
        """
        url = post.url

        if UrlUtils.is_image_url(url):
            criteria = TweetFinder.build_criteria_for_image(url)
        elif UrlUtils.is_imgur_url(url):
            criteria = TweetFinder.build_criteria_for_image(url)
        else:
            criteria = []

        return TweetFinder.find_tweets(criteria)

    def handle_tweet_result(self, post, tweets):
        """ Implements the actions made on new results

        Parameters
        ----------
        post : praw.submission
            The post the result was found for
        tweets : list
            results for the given post
        """
        if tweets and len(tweets) > 0:
            Logger.log_tweet_found(post.id, tweets[0].tweet.permalink)
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
        return Config.SINGLE_TWEET.format(index + 1, search_result.tweet.username, search_result.score,
                                          search_result.tweet.permalink) + "\n"
