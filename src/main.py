from realtweetornotbot import Bot
from realtweetornotbot.multithreading import MultiThreadSearcher


def main():
    print("Starting Bot\n")
    scheduler = MultiThreadSearcher(Bot())
    scheduler.schedule()
    print("Scheduler done - Workers running\n")


if __name__ == "__main__":
    main()
