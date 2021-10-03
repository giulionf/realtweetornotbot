from realtweetornotbot import Bot, DebugBot
from realtweetornotbot.bot import Config
from realtweetornotbot.multithreading import MultiThreadSearcher


def main():
    if Config.RUN_MODE == "release":
        print("MODE: Release")
        bot = Bot()
    else:
        print("MODE: Debug")
        bot = DebugBot()

    print("Starting Scheduler")
    scheduler = MultiThreadSearcher(bot)
    scheduler.schedule()
    print("Scheduler done - Workers running")


if __name__ == "__main__":
    main()
