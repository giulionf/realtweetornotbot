import psycopg2


class PostGresHelper:

    _connection = None
    _cursor = None

    def __init__(self, db_url, username, password):
        self._connection = psycopg2.connect(db_url, user=username, password=password)
        self._cursor = self._connection.cursor()

    def _execute(self, query):
        self._cursor.execute(query)

    def _fetch_all(self):
        return self._cursor.fetchall()

    def _fetch_one(self):
        return self._cursor.fetchone()

    def _commit(self):
        self._connection.commit()

    def close(self):
        self._cursor.close()
        self._connection.close()
