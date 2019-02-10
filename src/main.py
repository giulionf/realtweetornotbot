import os
import sys
import praw
import time
import traceback
import configparser
import concurrent.futures
from configparser import ExtendedInterpolation
from praw import exceptions
from realtweetornotbot.twitter.tweetfinder import TweetFinder

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
RESULT_MESSAGE = config['MESSAGE']['success']
WRONG_POST_TYPE_MESSAGE = config['MESSAGE']['wrong_type']
SINGLE_TWEET = config['MESSAGE']['single_tweet']

# Types of images that can be processed
ALLOWED_IMAGE_TYPES = ["jpg", "png", "jpeg", "webp"]

# Time to wait after a response request was denied until retrying
ATTEMPT_TIMEOUT = 30
MAX_TIMEOUT = 11 * 60

# Timeout after last comment streamed for remote hosting
NO_NEW_COMMENT_TIMEOUT = 10 * 60  # in seconds

# Number of concurrent threads
THREAD_POOL_COUNT = 5

# Praw Client
praw_client = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT, username=USERNAME,
                          password=PASSWORD)


def main():
    if is_run_locally():
        bot_loop_local()
    else:
        bot_loop_remote()


def debug(url):
    if is_image_submission(url):
        future_result = workers.submit(search_tweets, url)
        concurrent.futures.Future.add_done_callback(future_result, lambda x: debug_results(x.result()))
    elif is_imgur_submission(url):
        future_result = workers.submit(search_tweets, url + ".jpg")
        concurrent.futures.Future.add_done_callback(future_result, lambda x: debug_results(x.result()))
    else:
        print(WRONG_POST_TYPE_MESSAGE)


def debug_results(results):
    response = form_comment_response(results)
    print(response)


def bot_loop_local():
    print("STARTING BOT LOCALLY")
    for comment in praw_client.subreddit(SUBREDDITS).stream.comments():
        if should_summon(comment):
            on_summon(comment)


def bot_loop_remote():
    print("STARTING BOT ON REMOTE SERVER")
    for comment in praw_client.subreddit(SUBREDDITS).stream.comments():
        if should_summon(comment):
            on_summon(comment)


def on_summon(comment):
    print("New Comment From: {} in {}".format(comment.author.name, comment.subreddit.display_name))
    if comment.submission.url is not None:
        on_new_comment(comment)


def on_new_comment(comment):
    url = comment.submission.url
    if is_image_submission(url):
        dispatch_search_worker(comment, url)
    elif is_imgur_submission(url):
        dispatch_search_worker(comment, url + ".jpg")
    else:
        print(WRONG_POST_TYPE_MESSAGE)


def dispatch_search_worker(comment, image_url):
    print("Worker is dispatched")
    future_result = workers.submit(search_tweets, image_url)
    concurrent.futures.Future.add_done_callback(future_result, lambda x: on_new_result(comment, x.result()))


def on_new_result(comment, results):
    print("Worker Done: Trying to reply to {} in {}".format(comment.author.name, comment.subreddit.display_name))
    response = form_comment_response(results)
    try_repeatedly_with_timeout(lambda:  reply_to_comment(comment, response))


def reply_to_comment(comment, text):
    if should_summon(comment):
        comment.reply(text)
        comment.submission.save()
    else:
        print("Comment has been deleted or was changed... Shouldn't summon anymore!")


def search_tweets(image_url):
    results = TweetFinder.find_tweet_results(image_url)
    return results


def should_summon(comment):
    return KEYWORD in comment.body and not is_comment_from_bot(comment) \
           and not (comment.saved or comment.submission.saved)


def is_image_submission(url):
    return any(data_type in url for data_type in ALLOWED_IMAGE_TYPES)


def is_imgur_submission(url):
    return "imgur.com" in url


def is_comment_from_bot(comment):
    return str.lower(comment.author.name) == USERNAME


def send_pm_with_error_to_creator(error):
    last_100_pms = praw_client.inbox.sent(limit=100)
    is_old_error = any(pm.body == str(error) for pm in last_100_pms)

    if not is_old_error:
        praw_client.redditor(CREATOR_NAME).message("New error", str(error))


def try_repeatedly_with_timeout(func):
    start_time = time.time()
    too_many_tries_exception = True
    while too_many_tries_exception:
        try:
            too_many_tries_exception = False
            func()
        except Exception as e:
            if not isinstance(e, praw.exceptions.APIException) or time.time() - start_time >= MAX_TIMEOUT:
                send_pm_with_error_to_creator(traceback.format_exc())
                print("Error occured")
            else:
                too_many_tries_exception = True
                print("PRAW API Exception!: {}".format(str(e)))
                time.sleep(ATTEMPT_TIMEOUT)


def form_comment_response(results):
    return RESULT_MESSAGE.format(form_tweet_string(results))


def form_tweet_string(results):
    results = list(filter(lambda result: result.tweet is not None, results))
    if len(results) == 0:
        return "-"
    else:
        return "\n".join(list(map(lambda x: create_single_link_to_tweet(results.index(x), x), results)))


def create_single_link_to_tweet(index, result):
    return SINGLE_TWEET.format(index + 1, result.tweet.username, result.score, result.tweet.permalink) + "\n"


def is_run_locally():
    return len(sys.argv) > 1 and sys.argv[1] == "local"


if __name__ == "__main__":
    workers = concurrent.futures.ThreadPoolExecutor(THREAD_POOL_COUNT)
    main()
