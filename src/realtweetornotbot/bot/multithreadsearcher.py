from copy import deepcopy
from threading import Thread, Lock

WORKER_THREAD_LIMIT = 20  # Limit for the number of concurrently running worker threads

pop_lock = Lock()  # Lock for popping the top of the post_queue


class MultiThreadSearcher:
    """ Multi-threading scheduler for the bot """

    def __init__(self, bot):
        self.bot = bot
        self.post_queue = []
        self.workers = []

    def schedule(self):
        """ Fetches new posts. Uses the already running workers or starts new ones if needed """
        self.__get_new_posts()
        additional_workers_needed = min(WORKER_THREAD_LIMIT, len(self.post_queue)) - len(self.workers)
        if additional_workers_needed > 0:
            for i in range(0, additional_workers_needed):
                self.__create_new_worker()

    def remove_worker(self, worker):
        """ Removes a worker from the list of workers. Will not terminate that worker if it hasn't finished! """
        self.workers.remove(worker)
        print("Removed Workers, {} workers left".format(len(self.workers)))

    def pop_next_post(self):
        """ Pops the next post out of the post queue """
        pop_lock.acquire()
        if len(self.post_queue) > 0:
            post = self.post_queue[0]
            self.post_queue.remove(post)
        else:
            post = None
        pop_lock.release()
        return post

    def __get_new_posts(self):
        new_posts = self.bot.fetch_new_posts()
        self.post_queue.extend(new_posts)

    def __create_new_worker(self):
        assigned_post = self.pop_next_post()
        worker = MultiThreadSearcher.Worker(assigned_post, self, self.bot)
        self.workers.append(worker)
        worker.start()

    class Worker(Thread):
        """ Worker Thread for a post. Once it's done, it will reschedule itself with a new post or terminate """

        def __init__(self, post, scheduler, bot):
            super().__init__()
            self.post = post
            self.scheduler = scheduler
            self.bot = deepcopy(bot)

        def run(self) -> None:
            tweets = self.bot.find_tweet(self.post)
            self.bot.handle_tweet_result(self.post, tweets)

            next_post = self.scheduler.pop_next_post()
            if next_post is not None:
                self.__restart_with_new_post(next_post)
            else:
                self.scheduler.remove_worker(self)

        def __restart_with_new_post(self, post):
            self.post = post
            self.run()
