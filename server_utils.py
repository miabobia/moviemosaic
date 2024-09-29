'''
utility functions for server
USAGE: disco run --project [PROJECT_NAME] "python server_utils.py [cache/refresh]"

cache - displays contents of DB_CACHE table

refresh - removes rows from TASKS and RESULTS table. Displays how many rows were removed

'''


import sqlite3
import os
import sys
from dotenv import load_dotenv
if os.path.isfile('.env'):
    load_dotenv('.env')

db = sqlite3.connect(os.environ['DATABASE'])

def refresh_tables():
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) FROM TASKS")
    tasks_row_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM RESULTS")
    results_row_count = cur.fetchone()[0]

    db.execute("DROP TABLE IF EXISTS TASKS")
    db.execute("DROP TABLE IF EXISTS RESULTS")
    db.commit()
    cur.execute("CREATE TABLE IF NOT EXISTS TASKS(id, user, mode, progress_msg, status, error_msg)")
    cur.execute("CREATE TABLE IF NOT EXISTS RESULTS(id, result, created_on)")
    db.commit()
    db.close()

    print(f'removed {tasks_row_count} rows from TASKS')
    print(f'removed {results_row_count} rows from RESULTS')

def show_cache():
    cur = db.execute("SELECT * FROM DB_CACHE")
    rows = cur.fetchall()
    cur.close()
    for index, row in enumerate(rows):
        filename, blob, date = row
        print(f"{index:<5} {filename:<30} {len(blob):<12} {date:<20}")

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print(f'invalid number of args\n- (cache) display contents of cache\n- (refresh) refresh contents of TASKS and RESULTS table.')
    else:
        if args[0] == 'cache':
            pass
        elif args[0] == 'refresh':
            pass
        else:
            print(f'invalid arg `{args[0]}` passed\n- (cache) display contents of cache\n- (refresh) refresh contents of TASKS and RESULTS table.')