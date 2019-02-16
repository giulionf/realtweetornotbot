import time
from realtweetornotbot.bot.reddit.redditbotimpl import RedditBotImpl
from realtweetornotbot.bot.multithread import MultiThreadSearcher

SLEEP_TIME = 60 * 30


def main():
    MultiThreadSearcher.init(RedditBotImpl())

    while 1:
        MultiThreadSearcher.start()
        time.sleep(SLEEP_TIME)
        print("Job Done - Sleeping\n")


if __name__ == "__main__":
    main()
