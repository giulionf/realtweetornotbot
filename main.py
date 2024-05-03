import argparse
import logging
import os
import sys
from typing import Dict
import praw
import dotenv
from bot.bot import Bot
from persistance.database import Database


def main(args: Dict):
    logging.info(f"Starting with args: {args}")
    api = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"),
        username=os.getenv("REDDIT_USERNAME"),
        password=os.getenv("REDDIT_PASSWORD"),
    )
    db = Database()
    bot = Bot(api=api, db=db, subreddits="all")
    jobs = bot.fetch_jobs()
    for job in jobs:
        logging.info(job.get_post())


if __name__ == "__main__":
    dotenv.load_dotenv(".env", override=True)
    
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logging.info("Setup logger.")
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--loop", action="store_true", default="False")
    parser.add_argument("--debug", action="store_true", default="False")
    args = parser.parse_args()
    main(args)
