from realtweetornotbot import Bot, MultiThreadSearcher


def main():
    print("Starting Bot\n")
    scheduler = MultiThreadSearcher(Bot())
    scheduler.schedule()
    print("Scheduler done - Workers running\n")


if __name__ == "__main__":
    main()
