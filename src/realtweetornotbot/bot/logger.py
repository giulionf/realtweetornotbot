

class Logger:

    @staticmethod
    def log_fetch_count(fetch_count):
        print("<FETCHED POSTS> {} new posts. Dispatching workers!\n".format(fetch_count))

    @staticmethod
    def log_tweet_found(post_id, image_url):
        print("<WORKER - FOUND TWEET>\nPost: https://www.reddit.com/{}\nImage: {}\n".format(post_id, image_url))

    @staticmethod
    def log_no_results(post_id, image_url):
        print("<WORKER - NO RESULTS>\nPost: https://www.reddit.com/{}\nImage: {}\n".format(post_id, image_url))

    @staticmethod
    def log_error():
        print("[ERROR OCCURED] --> Sent PM with stacktrace!\n")

    @staticmethod
    def log_error_stacktrace(error_string):
        print("[EXCEPTION THROWN]\n{}\n".format(error_string))

    @staticmethod
    def log_db_deletion(delete_count):
        print("DB >>> Deleting last {} submission IDs\n".format(delete_count))

    @staticmethod
    def log_dispatching_threads(producer_count, consumer_count):
        print("<MAIN THREAD> Starting: Producers ({}) and Consumers ({})\n".format(producer_count, consumer_count))
