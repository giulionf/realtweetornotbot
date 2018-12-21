import os
import sys
import praw
import time
import traceback
import configparser
from configparser import ExtendedInterpolation
from praw import exceptions
from realtweetornotbot.twitter.tweetfinder import TweetFinder
from realtweetornotbot.comment.commandutils import CommandUtils
from realtweetornotbot.result.error import SearchError

config = configparser.ConfigParser()
config._interpolation = ExtendedInterpolation()
config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.ini"))

# Secret Data --> Create Environment Vars for these to use
USERNAME = os.environ['REDDIT_USERNAME']
PASSWORD = os.environ['REDDIT_PASSWORD']
CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
USER_AGENT = os.environ['REDDIT_USER_AGENT']

# Bot Data
CREATOR_NAME = config['BOTDATA']['creator']
KEYWORD = config['BOTDATA']['keyword']
SUBREDDITS = config['BOTDATA']['SUBREDDITS']

# Links
DONATE_LINK = config['LINKS']['donate']
SOURCE_LINK = config['LINKS']['source']
SUBREDDIT_LINK = config['LINKS']['subreddit']

# Message
SUCCESS_MESSAGE_BLUEPRINT = config['MESSAGE']['success']
NONE_FOUND_MESSAGE = config['MESSAGE']['none_found']
WRONG_POST_TYPE_MESSAGE = config['MESSAGE']['wrong_type']
SINGLE_TWEET = config['MESSAGE']['single_tweet']
ERROR_MESSAGE = config['MESSAGE']['error_occured']

# Error
NO_DATE_ERROR = config['ERROR']['no_date']
NO_USER_ERROR = config['ERROR']['no_user']
LOW_MATCH_ERROR = config['ERROR']['low_match']

# Types of images that can be processed
ALLOWED_IMAGE_TYPES = ["jpg", "png", "jpeg"]

# Time to wait after a response request was denied until retrying
ATTEMPT_TIMEOUT = 5

# Timeout after last comment streamed for remote hosting
NO_NEW_COMMENT_TIMEOUT = 10 * 60  # in seconds

# Praw Client
__client = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT, username=USERNAME,
                       password=PASSWORD)


def main():
    if is_run_locally():
        bot_loop_local()
    else:
        bot_loop_remote()


def bot_loop_local():
    print("STARTING BOT LOCALY")
    for comment in __client.subreddit(SUBREDDITS).stream.comments():
        if should_summon(comment):
            on_summon(comment)
            comment.save()


def bot_loop_remote():
    print("STARTING BOT ON REMOTE SERVER")
    for comment in __client.subreddit(SUBREDDITS).stream.comments():
        if should_summon(comment):
            on_summon(comment)
            comment.save()


def on_summon(comment):
    url = get_submission_link(comment)
    print("New Comment From: {} in {}".format(comment.author.name, comment.subreddit.display_name))
    if url is not None:
        try_repeatedly_with_timeout(lambda: write_reply(comment, url))


def should_summon(comment):
    return KEYWORD in comment.body and not is_comment_from_bot(comment) and not comment.saved


def is_image_submission(url):
    return any(data_type in url for data_type in ALLOWED_IMAGE_TYPES)


def is_comment_from_bot(comment):
    return str.lower(comment.author.name) == USERNAME


def write_reply(comment, url):
    print("Writing reply")
    if not is_image_submission(url):
        comment.reply(WRONG_POST_TYPE_MESSAGE)
    else:
        parameters = CommandUtils.get_comment_parameters(comment.body)
        results = TweetFinder.find_tweet_results(url, parameters)
        comment.reply(form_comment_response(results))
    print("Done writing reply")


def send_pm_with_error_to_creator(error):
    last_100_pms = __client.inbox.sent(limit=100)
    is_old_error = any(pm.body == str(error) for pm in last_100_pms)

    if not is_old_error:
        __client.redditor(CREATOR_NAME).message("New error", str(error))


def try_repeatedly_with_timeout(func):
    too_many_tries_exception = True
    while too_many_tries_exception:
        try:
            too_many_tries_exception = False
            func()
        except Exception as e:
            if not isinstance(e, praw.exceptions.APIException):
                send_pm_with_error_to_creator(traceback.format_exc())
                print("Error occured")
            else:
                too_many_tries_exception = True
                print("Waiting then trying again!: {}".format(str(e)))
                time.sleep(ATTEMPT_TIMEOUT)


def form_comment_response(results):
    if len(results) == 0:
        return NONE_FOUND_MESSAGE.format(form_none_found_message_body(results))
    else:
        return SUCCESS_MESSAGE_BLUEPRINT.format(form_success_message_body(results))


def form_none_found_message_body(results):
    if results and any(len(x.errors) > 0 for x in results):
        return form_error_message(results)
    else:
        return ""


def form_success_message_body(results):
    tweets_string = "\n".join(list(map(lambda x: create_single_link_to_tweet(results.index(x), x), results)))
    if any(len(x.errors) > 0 for x in results):
        tweets_string = tweets_string + "\n" + form_error_message(results)
    return tweets_string


def form_error_message(results):
    errors = []
    if any(SearchError.NO_USER in result.errors for result in results):
        errors.append(NO_USER_ERROR + "\n")

    if any(SearchError.NO_DATE in result.errors for result in results):
        errors.append(NO_DATE_ERROR + "\n")

    if any(SearchError.LOW_MATCH in result.errors for result in results):
        errors.append(LOW_MATCH_ERROR + "\n")

    return ERROR_MESSAGE.format("\n".join(errors))


def create_single_link_to_tweet(index, result):
    return SINGLE_TWEET.format(index + 1, result.tweet.username, result.score, result.tweet.permalink) + "\n"


def get_submission_link(comment):
    return comment.submission.url


def is_run_locally():
    return len(sys.argv) > 1 and sys.argv[1] == "local"


if __name__ == "__main__":
    main()
