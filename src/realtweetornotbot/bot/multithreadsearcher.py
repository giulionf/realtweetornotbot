from copy import deepcopy
from threading import Thread, Lock

WORKER_THREAD_LIMIT = 20  # Limit for the number of concurrently running worker threads

pop_lock = Lock()  # Lock for popping the top of the post_queue


class MultiThreadSearcher:
    """ Multi-threading scheduler for the bot """

    def __init__(self, bot):
        self.bot = bot
        self.job_queue = []
        self.workers = []

    def schedule(self):
        """ Fetches new posts. Uses the already running workers or starts new ones if needed """
        self.__get_new_jobs()
        additional_workers_needed = min(WORKER_THREAD_LIMIT, len(self.job_queue)) - len(self.workers)
        if additional_workers_needed > 0:
            for i in range(0, additional_workers_needed):
                self.__create_new_worker()

    def remove_worker(self, worker):
        """ Removes a worker from the list of workers. Will not terminate that worker if it hasn't finished! """
        self.workers.remove(worker)
        print("Removed Workers, {} workers left".format(len(self.workers)))

    def pop_next_job(self):
        """ Pops the next post out of the post queue """
        pop_lock.acquire()
        if len(self.job_queue) > 0:
            job = self.job_queue[0]
            self.job_queue.remove(job)
        else:
            job = None
        pop_lock.release()
        return job

    def __get_new_jobs(self):
        new_jobs = self.bot.fetch_new_jobs()
        self.job_queue.extend(new_jobs)

    def __create_new_worker(self):
        assigned_job = self.pop_next_job()
        worker = MultiThreadSearcher.Worker(assigned_job, self, self.bot)
        self.workers.append(worker)
        worker.start()

    class Worker(Thread):
        """ Worker Thread for a post. Once it's done, it will reschedule itself with a new post or terminate """

        def __init__(self, job, scheduler, bot):
            super().__init__()
            self.job = job
            self.scheduler = scheduler
            self.bot = deepcopy(bot)

        def run(self) -> None:
            tweets = self.bot.find_tweet(self.job)
            self.bot.handle_tweet_result(self.job, tweets)

            next_job = self.scheduler.pop_next_job()
            if next_job is not None:
                self.__restart_with_new_job(next_job)
            else:
                self.scheduler.remove_worker(self)

        def __restart_with_new_job(self, job):
            self.job = job
            self.run()
