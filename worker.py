'''
Background worker that will check/execute tasks in database 
'''
import sqlite3
import os
from collections import deque

DATABASE = "./sqlitedata/database.sqlite3" if os.path.isfile('.env') else "/sqlitedata/database.sqlite3"


def get_new_tasks(db: sqlite3.Connection) -> list:
    # check if there is a new task in TASKS
    cur = db.execute("SELECT * FROM TASKS WHERE STATUS = ?", ("READY"))
    rows = cur.fetchall()
    cur.close()
    return rows

def update_task_status(db: sqlite3.Connection, task_id: str, status: str, error_msg: str = None):
    if error_msg:
        # put error message here
        pass
    cur = db.execute("UPDATE TASKS SET STATUS = ? WHERE ID = ?", (status, task_id))
    cur.close()
    db.commit()

def run_task(task: str) -> (bool, any):
    # match case to interpret what task to be run?
    pass

def main():

    # assuming TASKS table already exists
    db = sqlite3.connect(DATABASE)
    tasks = deque()
    while True:
        # get new tasks
        new_tasks = get_new_tasks(db)

        # set status of all new tasks to queued
        for task in new_tasks:
            tasks.append(task)
            update_task_status(db, task[0], 'QUEUED')

        # see if any tasks exist
        if not tasks:
            continue

        # run current task
        result, data = run_task(tasks[0])
        curr_task = tasks.popleft()

        # task is complete update TASKS table
        if not result:
            # push error to TASKS table
            continue
        update_task_status(db, curr_task[0], 'COMPLETE')

        # push result to RESULTS table


if __name__ == '__main__':
    main()