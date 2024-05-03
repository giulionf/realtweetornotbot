

import logging
from typing import List

import psycopg2

from src.realtweetornotbot.bot.config import Config
from src.realtweetornotbot.bot.job import BaseJob
from src.realtweetornotbot.twittersearch.searchresult import TweetCandidate


class Database:
    """ Database for logging bot data """
    
    def on_job_done(self, job: BaseJob, result: List[TweetCandidate]) -> None:
        logging.info(f"DB_ON_JOB_DONE={job}, {result}")
        
    def filter_unique_novel_jobs(self, jobs: List[BaseJob]) -> List[BaseJob]:
        logging.info(f"DB_FILTER_UNIQUE_NOVEL_JOBS={jobs}")
        return jobs
    
    
class PostgresDatabase(Database):
    
    def __init__(self, url: str, user: str, password: str):
        self.__connection = psycopg2.connect(url,
                                             user=user,
                                             password=password)
        self.__cursor = self.__connection.cursor()
        
    def on_job_done(self, job: BaseJob, result: List[TweetCandidate]) -> None:
        submission_id = str(job.get_post().submission_id)
        tweet_link = "" if len(result) == 0 else result[0].tweet.url
        self.__cursor.execute(f"INSERT INTO seen_posts (post_id, found_tweet) VALUES ('{submission_id}', '{tweet_link}');")
        self.__connection.commit()
        
    def filter_unique_novel_jobs(self, jobs: List[BaseJob]) -> List[BaseJob]:
        submission_ids = [j.get_post().submission_id for j in jobs]
        sql = "SELECT * FROM seen_posts WHERE post_id in (%s);"
        self.__cursor.execute(sql, ", ".join(submission_ids))
        
        filtered_jobs = []
        for job in jobs:
            # TODO
            filtered_jobs.append(job)
        return filtered_jobs
