'''
so i can remotely monitor my db_cache
USAGE: disco run --project moviemosaic "python show_db_cache.py"
'''

import sqlite3
import os
import time
from dotenv import load_dotenv
if os.path.isfile('.env'):
    load_dotenv('.env')

db = sqlite3.connect(os.environ['DATABASE'])
def show():
    cur = db.execute("SELECT * FROM DB_CACHE")
    rows = cur.fetchall()
    cur.close()
    print(f"{'Index':<5} {'Filename':<30} {'Blob Length':<12} {'Date':<20}")
    print("="*67)

    # Print each row
    for index, row in enumerate(rows):
        filename, blob, date = row
        print(f"{index:<5} {filename:<30} {len(blob):<12} {date:<20}")


if __name__ == '__main__':
    while True:
        show()
        time.sleep(30)