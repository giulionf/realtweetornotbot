from realtweetornotbot import DebugBot
from realtweetornotbot.multithreading import MultiThreadSearcher


def main():
    print("Starting Bot in Debug Mode\n")
    scheduler = MultiThreadSearcher(DebugBot())
    scheduler.schedule()
    print("Scheduler done - Workers running\n")


if __name__ == "__main__":
    main()
