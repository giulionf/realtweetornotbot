from queue import Queue
from threading import Thread, Lock

PRODUCER_THREAD_COUNT = 20
CONSUMER_THREAD_COUNT = 1

post_queue = Queue()
result_queue = Queue()
bot_interface = None
debug = False


class MultiThreadSearcher:

    tesseract_lock = Lock()

    @staticmethod
    def init(bot_interface_impl, debug_mode=False):
        global debug
        global bot_interface
        bot_interface = bot_interface_impl
        debug = debug_mode

        for i in range(0, PRODUCER_THREAD_COUNT):
            ProducerThread().start()

        for i in range(0, CONSUMER_THREAD_COUNT):
            ConsumerThread().start()

    @staticmethod
    def start():
        global bot_interface
        global post_queue
        global result_queue

        new_posts = bot_interface.fetch_new_posts()
        for new_post in new_posts:
            post_queue.put(new_post)

        post_queue.join()
        result_queue.join()


class ProducerThread(Thread):
    def run(self):
        while True:
            global post_queue
            global bot_interface

            post = post_queue.get()
            post_queue.task_done()

            if post is None:
                break

            tweets = bot_interface.find_tweet(post)
            result_queue.put((post, tweets))


class ConsumerThread(Thread):
    def run(self):
        global result_queue
        global bot_interface
        global debug

        while True:
            result = result_queue.get()

            if result is None:
                break

            if debug:
                print(result[1])
            else:
                bot_interface.handle_tweet_result(result[0], result[1])
            result_queue.task_done()
