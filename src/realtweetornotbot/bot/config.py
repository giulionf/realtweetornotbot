import os
from configparser import ConfigParser, ExtendedInterpolation


class Config:
    """ Holds all the configureations for a bot """
    config = ConfigParser()
    config._interpolation = ExtendedInterpolation()
    config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../config.ini"))

    USERNAME = os.environ['REDDIT_USERNAME']
    PASSWORD = os.environ['REDDIT_PASSWORD']
    CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
    CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
    USER_AGENT = os.environ['REDDIT_USER_AGENT']
    SUBREDDITS = os.environ['REDDIT_SUBREDDITS']
    FETCH_COUNT = int(os.environ['REDDIT_FETCH_COUNT'])
    SUMMON_COUNT = int(os.environ['REDDIT_SUMMON_COUNT'])
    POST_MAX_AGE_DAYS = int(os.environ['REDDIT_POST_MAX_AGE_DAYS'])

    # Bot Data
    CREATOR_NAME = config['BOTDATA']['creator']

    # Links
    SOURCE_LINK = config['LINKS']['source']
    SUBREDDIT_LINK = config['LINKS']['subreddit']

    # Message
    RESULT_MESSAGE = config['MESSAGE']['success']
    WRONG_POST_TYPE_MESSAGE = config['MESSAGE']['wrong_type']
    SINGLE_TWEET = config['MESSAGE']['single_tweet']

    # Database
    DATABASE_URL = os.environ['DATABASE_URL']
    DATABASE_USER = os.environ['DATABASE_USER']
    DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
    DATABASE_MAX_POSTS = 9000
    DATABASE_MAX_SUMMARIES = 100
    DATABASE_SUMMARY_INTERVAL_HOURS = 24
