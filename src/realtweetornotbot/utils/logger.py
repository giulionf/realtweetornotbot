import threading


class Logger:
    """ Helper class for Logging to the console """

    @staticmethod
    def log_fetch_count(fetch_count):
        """ Logs the amount of posts that have been fetched """
        print("<FETCHED POSTS> {} new posts. Dispatching workers!\n".format(fetch_count))

    @staticmethod
    def log_summon_count(fetch_count):
        """ Logs the amount of comment mentions that have been fetched """
        print("<FETCHED SUMMONS> {} new summons. Dispatching workers!\n".format(fetch_count))

    @staticmethod
    def log_tweet_found(post_id, image_url):
        """ Logs that a tweet to a given post_id has been found """
        print("<WORKER-{} - FOUND TWEET>\nPost: https://www.reddit.com/{}\nTweet: {}\n"
              .format(threading.currentThread().getName(), post_id, image_url))

    @staticmethod
    def log_no_results(post_id, image_url):
        """ Logs that a worker has not found any tweet result for a given post_id """
        print("<WORKER-{} - NO RESULTS>\nPost: https://www.reddit.com/{}\nImage: {}\n"
              .format(threading.currentThread().getName(), post_id, image_url))

    @staticmethod
    def log_error():
        """ Logs and error in the main loop """
        print("[ERROR OCCURED] --> Sent PM with stacktrace!\n")

    @staticmethod
    def log_error_stacktrace(error_string):
        """ Logs and error with the given stacktrace """
        print("[EXCEPTION THROWN]\n{}\n".format(error_string))

    @staticmethod
    def log_db_deletion(delete_count):
        """ Logs the deletion of rows inside the Database """
        print("DB >>> Deleting last {} submission IDs\n".format(delete_count))

    @staticmethod
    def log_db_summary_deletion():
        """ Logs the deletion of a summary inside the Database """
        print("DB >>> Deleting last summary\n")

    @staticmethod
    def log_dispatching_threads(producer_count, consumer_count):
        """ Logs the dispatching of worker threads """
        print("<MAIN THREAD> Starting: Producers ({}) and Consumers ({})\n".format(producer_count, consumer_count))

    @staticmethod
    def log_summary_time(timedelta):
        """ Logs the time difference between now and the last summary time """
        print("<MAIN THREAD> Time Diff to last summary: {}".format(str(timedelta)))
