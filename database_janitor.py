'''
database_janitor -> emoji was here
cleans up the shared sqlite3 database
'''

import sqlite3
from datetime import datetime, timedelta
import os
from time import sleep

DATABASE = "./sqlitedata/database.sqlite3" if os.path.isfile('.env') else "/sqlitedata/database.sqlite3"
EXPIRY_TIME = 120 #43200 # how many seconds until result is expired

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
    return rows

def get_expired_tasks(db: sqlite3.Connection) -> list:
    '''
    Returns list of all task_id's that are expired
    '''
    results = get_results(db)
    expired_task_ids = []
    if not results:
        return []
    now = datetime.now()
    for row in results:
        task_id, _, created_on = row
        created_date = datetime.strptime(created_on, '%Y-%m-%d %H:%M:%S')
        # if now - created_date > timedelta(seconds=EXPIRY_TIME):
        if True:
            expired_task_ids.append(task_id)
    return expired_task_ids

def remove_expired_tasks(db: sqlite3.Connection):
    '''
    Removes all expired tasks from RESULTS and TASKS table
    returns how many expired id's were found (and hopefully removed)
    '''

    expired_ids = get_expired_tasks(db)
    if not expired_ids:
        return 0

    placeholders = ','.join('?' for _ in expired_ids)
    db.execute(f"""
        DELETE FROM TASKS
        WHERE ID IN ({placeholders})
    """, expired_ids)

    db.execute(f"""
        DELETE FROM RESULTS
        WHERE ID IN ({placeholders})
    """, expired_ids)

    db.commit()

    return len(expired_ids)

def main(db: sqlite3.Connection):

    while True:
        sleep(1)
        remove_expired_tasks(db)

if __name__ == '__main__':

    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS TASKS(id, user, mode, progress_msg, status, error_msg)")
    cur.execute("CREATE TABLE IF NOT EXISTS RESULTS(id, result, created_on)")
    cur.close()
    db.commit()
    # remove_expired_tasks(db)
    # db.commit()
    main(db)

# }, "minutecron": {
#     "type": "cron",
#     "schedule": "* * * * *",
#     "command": "python database_janitor.py",
#     "volumes": [
#         {
#             "name": "sqlite-data",
#             "destinationPath": "/sqlitedata"
#         }
#     ]
# }