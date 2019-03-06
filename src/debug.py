from realtweetornotbot.bot.debug.debugbotimpl import DebugBotImpl
from realtweetornotbot.bot.multithread import MultiThreadSearcher


def main():
    MultiThreadSearcher.init(DebugBotImpl())
    MultiThreadSearcher.start()
    print("Job Done - Waiting for next schedule\n")


if __name__ == "__main__":
    main()
