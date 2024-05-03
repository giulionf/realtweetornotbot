from bot import Bot


def main():
    run_once()

    # If infinite mode is on, run again in a loop
    while Config.RUN_INFINITELY == 1:
        run_once()


def run_once():
    bot = get_bot_instance()
    print("Starting Scheduler")
    scheduler = MultiThreadSearcher(bot)
    scheduler.schedule()
    print("Scheduler done - Workers running")


def get_bot_instance():
    if Config.RUN_MODE == "release":
        print("MODE: Release")
        bot = Bot()
    else:
        print("MODE: Debug")
        bot = DebugBot()
    return bot


if __name__ == "__main__":
    main()
