'''
dcCache class:
stores (_max_size) images as binary blobs in a lookup table.
can be used to cache images
main purpose is for movie posters that need downloading constantly
called by worker.py->fetch_data.py. worker only has one 'thread' running at a time so there shouldn't be any threat of
deleted data as it is needed in image_builder.py which is also handled by worker.py

rows in 'DB_CACHE' table are structured like this | FILENAME: str | IMAGEBLOB: BLOB| LAST_USED_DATE: str(datetime) |
'''

import sqlite3
from datetime import datetime


class dbCache:
    _max_size: int
    _db: sqlite3.Connection
    def __init__(self, max_size, db:sqlite3.Connection) -> None:
        self._max_size = max_size
        self._db = db

    def lookup(self, filename: str) -> bool:
        '''
        looks up filename and returns true or false.
        if the filename is true then the driving code needs to call dbCache.push()
        '''
        cur = self._db.execute('SELECT * FROM DB_CACHE where FILENAME = ?', (filename,))
        data = cur.fetchone()
        cur.close()

        if not data:
            return False
        

        self._db.execute(
        """UPDATE DB_CACHE
        SET LAST_USED_DATE = ?
        WHERE FILENAME = ?
        """,
        (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), filename)
        )

        self._db.commit()

        return True
    
    def push(self, filename: str, image_data: bytes) -> int:

        table_count = self.get_count()

        # see if we need to remove any data to keep table in max_size
        if table_count >= self._max_size:
            cur = self._db.execute("""
            SELECT FILENAME
            FROM DB_CACHE
            ORDER BY LAST_USED_DATE ASC
            LIMIT 1
            """)

            old_filename = cur.fetchone()[0]

            self._db.execute("""
            DELETE FROM DB_CACHE
            WHERE FILENAME = ?
            """,
            (old_filename,))

        self._db.execute("""
        INSERT INTO DB_CACHE
        VALUES (?, ?, ?)
        """,
        (filename, image_data, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        return table_count # putting this here to be useful for debugging later


    def get_count(self) -> int:

        cur = self._db.execute('SELECT COUNT(*) FROM DB_CACHE')
        count = cur.fetchone()
        cur.close()
        if not count:
            return -1
        return count[0]