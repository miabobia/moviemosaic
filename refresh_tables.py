'''
so i can remotely clear the tables using disco's cli run command
USAGE: disco run --project moviemosaic "python refresh_tables.py"
'''

import sqlite3
import os
from dotenv import load_dotenv
if os.path.isfile('.env'):
    load_dotenv('.env')

db = sqlite3.connect(os.environ['DATABASE'])

db.execute("DROP TABLE IF EXISTS TASKS")
db.execute("DROP TABLE IF EXISTS RESULTS")
db.commit()
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS TASKS(id, user, mode, progress_msg, status, error_msg)")
cur.execute("CREATE TABLE IF NOT EXISTS RESULTS(id, result, created_on)")
db.commit()
db.close()