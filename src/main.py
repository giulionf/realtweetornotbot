from realtweetornotbot.bot.reddit.redditbotimpl import RedditBotImpl
from realtweetornotbot.bot.multithread import MultiThreadSearcher


def main():
    MultiThreadSearcher.init(RedditBotImpl())
    MultiThreadSearcher.start()
    print("Job Done - Waiting for next schedule\n")


if __name__ == "__main__":
    main()
