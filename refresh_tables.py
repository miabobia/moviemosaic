import sqlite3


db = sqlite3.connect("/sqlitedata/database.sqlite3")

db.execute("DROP TABLE IF EXISTS TASKS")
db.execute("DROP TABLE IF EXISTS RESULTS")
db.commit()
cur = db.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS TASKS(id, user, mode, progress_msg, status, error_msg)")
cur.execute("CREATE TABLE IF NOT EXISTS RESULTS(id, result, created_on)")
db.commit()
db.close()