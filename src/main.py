import os
import sys
import praw
import time
import traceback
import configparser
import concurrent.futures
from configparser import ExtendedInterpolation
from praw import exceptions
from realtweetornotbot.search.tweetfinder import TweetFinder

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

# Timeout after last submission streamed for remote hosting
RUN_TIMEOUT = 30 * 60  # half hour between each run

POST_FETCH_COUNT = 100  # Total number of fetched posts! Not per subreddit

# Number of concurrent threads
THREAD_POOL_COUNT = 3

# Praw Client
praw_client = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT, username=USERNAME,
                          password=PASSWORD)


def main():
    while 1:
        on_bot_scheduled()
        time.sleep(RUN_TIMEOUT)


def debug(url):
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL_COUNT) as workers:
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


def on_bot_scheduled():
    image_submissions = []
    for submission in praw_client.subreddit(SUBREDDITS).hot(limit=POST_FETCH_COUNT):
        if should_summon(submission):
            image_submissions.append(submission)

    print("Checking {} submissions".format(len(image_submissions)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL_COUNT) as workers:
        workers.map(on_new_submission, image_submissions)
    print("Job Done - Sleeping")


def on_new_submission(submission):
    if is_image_submission(submission.url):
        print("Image Submission From: {} in {}".format(submission.author.name, submission.subreddit.display_name))
        on_new_result(submission, search_tweets(submission.url))
    elif is_imgur_submission(submission.url):
        print("IMGUR Submission From: {} in {}".format(submission.author.name, submission.subreddit.display_name))
        on_new_result(submission, search_tweets(submission.url + ".jpg"))


def on_submission_done(submission):
    submission.save()


def on_new_result(submission, results):
    if len(results) > 0:
        print("Worker Done: Replying to {} in {}".format(submission.author.name, submission.subreddit.display_name))
        response = form_comment_response(results)
        try_repeatedly_with_timeout(lambda:  reply_to_submission(submission, response))
    else:
        print("No results for submission by {} in {}".format(submission.author.name, submission.subreddit.display_name))
    on_submission_done(submission)


def reply_to_submission(submission, text):
    if should_summon(submission):
        submission.reply(text)


def search_tweets(image_url):
    print("Searching Tweet in Worker: {}".format(image_url))
    results = TweetFinder.find_tweets(image_url)
    return results


def should_summon(submission):
    return not submission.saved and submission.url is not None


def is_image_submission(url):
    return any(data_type in url for data_type in ALLOWED_IMAGE_TYPES)


def is_imgur_submission(url):
    return "imgur.com" in url


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
    return "\n".join(list(map(lambda x: create_single_link_to_tweet(results.index(x), x), results)))


def create_single_link_to_tweet(index, result):
    return SINGLE_TWEET.format(index + 1, result.tweet.username, result.score, result.tweet.permalink) + "\n"


def is_run_locally():
    return len(sys.argv) > 1 and sys.argv[1] == "local"


if __name__ == "__main__":
    main()
