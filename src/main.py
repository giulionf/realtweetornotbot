from realtweetornotbot import Bot, MultiThreadSearcher


def main():
    print("Starting Bot\n")
    MultiThreadSearcher.init(Bot())
    MultiThreadSearcher.start()
    print("Job Done - Waiting for next schedule\n")


if __name__ == "__main__":
    main()
