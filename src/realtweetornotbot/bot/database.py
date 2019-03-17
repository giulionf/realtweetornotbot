import psycopg2
from datetime import datetime
from realtweetornotbot.bot import Config
from realtweetornotbot.utils import Logger


class Database:
    """ Database for logging bot data """

    __connection = None
    __cursor = None

    def __init__(self):
        self.__connection = psycopg2.connect(Config.DATABASE_URL,
                                             user=Config.DATABASE_USER,
                                             password=Config.DATABASE_PASSWORD)
        self.__cursor = self.__connection.cursor()

    def add_submission_to_seen(self, submission_id, tweet_link=""):
        """ Adds a submission ID with the resulting tweet link to the seen_posts table """
        self.__cursor.execute("INSERT INTO seen_posts (post_id, found_tweet) VALUES ('{}', '{}');"
                              .format(str(submission_id), tweet_link))
        self.__connection.commit()

    def is_submission_already_seen(self, submission_id):
        """ Returns true, if the submission_id has already been visited before """
        self.__cursor.execute("""SELECT * FROM seen_posts WHERE post_id = %s""", (submission_id,))
        result = self.__cursor.fetchall()
        return len(result) > 0

    def delete_old_entries_if_db_full(self, new_entries_count):
        """ Makes space in the database if the new post addition would overstep the total row limit """
        self.__cursor.execute("SELECT COUNT(post_id) FROM seen_posts;")
        cur_entries = int(self.__cursor.fetchone()[0])
        if cur_entries + new_entries_count >= Config.DATABASE_MAX_POSTS:
            Logger.log_db_deletion(new_entries_count)
            self.__cursor.execute("DELETE FROM seen_posts WHERE id IN (SELECT id FROM seen_posts ORDER BY id ASC LIMIT {});".format(new_entries_count))
            self.__connection.commit()

    def delete_old_summaries_if_db_full(self):
        self.__cursor.execute("""SELECT COUNT(id) FROM summary""")
        cur_entries = int(self.__cursor.fetchone()[0])
        if cur_entries >= Config.DATABASE_MAX_SUMMARIES:
            Logger.log_db_summary_deletion()
            self.__cursor.execute("""DELETE FROM summary WHERE id IN (SELECT id FROM summary ORDER BY id ASC LIMIT 1)""")

    def get_time_diff_since_last_summary(self):
        """ Returns the time diff to the last summary"""
        self.__cursor.execute("SELECT time FROM summary ORDER BY time DESC LIMIT 1;")
        last_time = self.__cursor.fetchone()[0]
        return datetime.now() - last_time

    def get_summary(self):
        """ Returns the last summary as a tuple: (int, int) -> (posts_seen, tweets_found) """
        self.__cursor.execute("SELECT COUNT(*) FROM seen_posts WHERE id > (SELECT last_post_id FROM summary ORDER BY time DESC LIMIT 1);")
        posts_seen = self.__cursor.fetchone()[0]
        self.__cursor.execute("SELECT COUNT(*) FROM seen_posts WHERE found_tweet IS NOT NULL AND NOT found_tweet = '' AND id > (SELECT last_post_id FROM summary ORDER BY time DESC LIMIT 1);")
        tweets_found = self.__cursor.fetchone()[0]
        return posts_seen, tweets_found

    def persist_summary(self, summary):
        """ Writes a newly made summary into the summary table """
        self.__cursor.execute("INSERT INTO summary(posts_seen, tweets_found, last_post_id) VALUES({}, {}, (SELECT id FROM seen_posts ORDER BY id DESC LIMIT 1));".format(summary[0], summary[1]))
        self.__connection.commit()
