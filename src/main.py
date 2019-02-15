import time
from realtweetornotbot.bot.reddit.redditbotimpl import RedditBotImpl

SLEEP_TIME = 60 * 30


def main():
    bot = RedditBotImpl()

    while 1:
        posts = bot.fetch_new_posts()
        for post in posts:
            tweets = bot.find_tweet(post)
            bot.handle_tweet_result(post, tweets)
        time.sleep(SLEEP_TIME)
        print("Job Done - Sleeping")


if __name__ == "__main__":
    main()
