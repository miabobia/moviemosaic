'''
database_janitor -> 👱‍♀️🧹
cleans up the shared sqlite3 database
'''

import sqlite3
from datetime import datetime

DATABASE = "./sqlitedata/database.sqlite3" if os.path.isfile('.env') else "/sqlitedata/database.sqlite3"
EXPIRY_TIME = 60 #43200 # how many seconds until result is expired
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

def get_expired_tasks(db: sqlite3.Connection) -> list:
    '''
    Returns list of all task_id's that are expired
    '''
    results = get_results(db)
    expired_task_ids = []
    if not results:
        return []
    now = datetime.now().strftime('%Y-%m-%d')
    for row in results:
        task_id, _, created_on = row
        if now - created_on > EXPIRY_TIME:
            expired_task_ids.append(task_id)
    return expired_task_ids

def remove_expired_tasks(db: sqlite3.Connection):
    '''
    Removes all expired tasks from RESULTS and TASKS table
    returns how many expired id's were found (and hopefully removed)
    '''

    expired_ids = get_expired_tasks(db)

    # make list of task_ids to delete that sqlite3 can parse
    placeholders = ','.join(['?'] * len(expired_ids))
    db.execute("""
        DELETE FROM TASKS
        WHERE ID IN ?
    """, placeholders)

    db.execute("""
        DELETE FROM RESULTS
        WHERE ID IN ?
    """, placeholders)

    db.commit()

    return len(expired_ids)

if __name__ == '__main__':
    db = sqlite3.connect(DATABASE)
    remove_expired_tasks(db)
    db.close()