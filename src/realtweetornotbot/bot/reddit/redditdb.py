from realtweetornotbot.persist.postgreshelper import PostGresHelper
from realtweetornotbot.bot.reddit.config import Config
from realtweetornotbot.bot.logger import Logger
from datetime import datetime


class RedditDB(PostGresHelper):

    def __init__(self):
        super().__init__(Config.DATABASE_URL, Config.DATABASE_USER, Config.DATABASE_PASSWORD)

    def add_submission_to_seen(self, submission_id, tweet_link=""):
        self._execute("INSERT INTO seen_posts (post_id, found_tweet) VALUES ('{}', '{}');"
                      .format(str(submission_id), tweet_link))
        self._commit()

    def is_submission_already_seen(self, submission_id):
        self._execute("SELECT * FROM seen_posts".format(str(submission_id)))
        result = self._fetch_all()
        return len(result) > 0 and str(submission_id) in [x[0] for x in result]

    def delete_old_entries_if_db_full(self, new_entries_count):
        self._execute("SELECT COUNT(post_id) FROM seen_posts;")
        cur_entries = int(self._fetch_one()[0])
        if cur_entries + new_entries_count >= Config.DATABASE_MAX_ROWS - Config.DATABASE_FULL_PADDING:
            Logger.log_db_deletion(new_entries_count)
            self._execute("DELETE FROM seen_posts WHERE id IN (SELECT id FROM seen_posts ORDER BY id ASC LIMIT {});"
                          .format(new_entries_count))
            self._commit()

    def get_time_diff_since_last_summary(self):
        self._execute("SELECT time FROM summary ORDER BY time DESC LIMIT 1;")
        last_time = self._fetch_one()[0]
        return datetime.now() - last_time

    def get_summary(self):
        self._execute("SELECT COUNT(*) FROM seen_posts WHERE id > (SELECT last_post_id FROM summary ORDER BY time DESC LIMIT 1);")
        posts_seen = self._fetch_one()[0]
        self._execute("SELECT COUNT(*) FROM seen_posts WHERE found_tweet IS NOT NULL AND NOT found_tweet = '' AND id > (SELECT last_post_id FROM summary ORDER BY time DESC LIMIT 1);")
        tweets_found = self._fetch_one()[0]
        return posts_seen, tweets_found

    def persist_summary(self, summary):
        self._execute("INSERT INTO summary(posts_seen, tweets_found) VALUES({}, {});".format(summary[0], summary[1]))
        self._commit()
