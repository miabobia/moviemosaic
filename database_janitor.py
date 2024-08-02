'''
databse_janitor -> 👱‍♀️🧹
cleans up the shared sqlite3 database
'''

import sqlite3
from datetime import datetime

DATABASE = "./sqlitedata/database.sqlite3" if os.path.isfile('.env') else "/sqlitedata/database.sqlite3"
EXPIRY_TIME = 43200 # how many seconds until result is expired
def get_results(db: sqlite3.Connection):
    '''
    Fetches all rows from RESULTS table.
    (TASK_ID, RESULT(IMAGE_STRING), CREATED_ON)
    '''
    cur = db.execute(
        """
        SELECT * FROM RESULTS
        """
        )
    rows = cur.fetchall()
    cur.close()

def get_expired_tasks(db: sqlite3.Connection, result_func: function) -> list:
    '''
    Returns list of all task_id's that are expired
    '''
    results = result_func(db)
    if not results:
        return []
    now = datetime.now()
    for row in results:
        task_id, _, created_on = row
    


def main(db: sqlite3.Connection):
    pass




if __name__ == '__main__':
    db = sqlite3.connect(DATABASE)
    main(db)