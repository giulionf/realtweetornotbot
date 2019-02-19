from realtweetornotbot.persist.postgreshelper import PostGresHelper
from realtweetornotbot.bot.reddit.config import Config


class RedditDB(PostGresHelper):

    def __init__(self):
        super().__init__(Config.DATABASE_URL, Config.DATABASE_USER, Config.DATABASE_PASSWORD)

    def add_submission_to_seen(self, submission_id):
        self._execute("INSERT INTO seen_posts (post_id) VALUES ('{}');".format(str(submission_id)))
        self._commit()

    def is_submission_already_seen(self, submission_id):
        self._execute("SELECT * FROM seen_posts".format(str(submission_id)))
        result = self._fetch_all()
        return len(result) > 0 and str(submission_id) in [x[0] for x in result]

    def delete_old_entries_if_db_full(self, new_entries_count):
        self._execute("SELECT COUNT(post_id) FROM seen_posts;")
        cur_entries = int(self._fetch_one()[0])
        if cur_entries + new_entries_count >= Config.DATABASE_MAX_ROWS - Config.DATABASE_FULL_PADDING:
            print("DELETING LAST {} DB ENTRIES TO MAKE ROOM".format(new_entries_count))
            self._execute("DELETE FROM seen_posts WHERE id IN (SELECT id FROM seen_posts ORDER BY id ASC LIMIT {});"
                          .format(new_entries_count))
            self._commit()

