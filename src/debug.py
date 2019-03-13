from realtweetornotbot import DebugBot, MultiThreadSearcher


def main():
    print("Starting Bot in Debug Mode\n")
    MultiThreadSearcher.init(DebugBot())
    MultiThreadSearcher.start()
    print("Bot Done")


if __name__ == "__main__":
    main()
