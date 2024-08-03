'''
Background worker that will check/execute tasks in database 
'''
import sqlite3
import os
from collections import deque
from time import sleep
from fetch_data import MovieCellBuilder
from image_builder import build
from datetime import datetime
import io
import base64

DATABASE = "./sqlitedata/database.sqlite3" if os.path.isfile('.env') else "/sqlitedata/database.sqlite3"


def get_new_tasks(db: sqlite3.Connection) -> list:
    # check if there is a new task in TASKS
    cur = db.execute("SELECT * FROM TASKS WHERE STATUS = ?", ("READY",))
    rows = cur.fetchall()
    cur.close()
    return rows

def update_task_status(db: sqlite3.Connection, task_id: str, status: str, progress_msg: str, error_msg: str = 'NULL'):

    db.execute(
        """UPDATE TASKS 
        SET STATUS = ?,
        PROGRESS_MSG = ?,
        ERROR_MSG = ?
        WHERE ID = ?""",
        (status, progress_msg, error_msg, task_id))

    db.commit()

def push_result(db: sqlite3.Connection, task_id: str, result: str):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute(
        """
        INSERT INTO RESULTS
        VALUES (?, ?, ?)
        """,
        (task_id, result, now)
        )
    db.commit()

def main(db: sqlite3.Connection):
    tasks = deque()
    while True:
        sleep(1)
        # get new tasks
        new_tasks = get_new_tasks(db)

        # set status of all new tasks to queued
        for task in new_tasks:
            tasks.append(task)
            update_task_status(db, task[0], 'QUEUED', 'WAITING')

        # see if any tasks exist
        if not tasks:
            continue
        
        # task is starting to we change its status immediately to reflect change on front end
        update_task_status(db, tasks[0][0], 'COLLECTING DATA', 'COLLECTING DATA')

        # 
        movie_cell_builder = MovieCellBuilder(
            username = tasks[0][1],
            mode = int(tasks[0][2])
        )

        status, err = movie_cell_builder.get_status()

        # username is no good
        if not status:
            update_task_status(db, tasks[0][0], 'ERROR', 'ERROR', err)
            push_result(db, tasks[0][0], 'NULL')
            tasks.popleft()
            continue

        movie_cells = movie_cell_builder.build_cells()

        # task is building image now
        update_task_status(db, tasks[0][0], 'BUILDING MOSAIC', 'BUILDING MOSAIC')
        image = build(
            movie_cells=movie_cells,
            username=tasks[0][1],
            config_path='config.json',
            last_watch_date=movie_cell_builder.get_last_movie_date()
            )
        
        # image has been built now we need to store it in RESULTS table
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
       # push_result(db, task[0][0], image_string)
        push_result(db, tasks[0][0], image_string)


        # mark task as complete
        update_task_status(db, tasks[0][0], 'COMPLETE', 'MOSAIC FINISHED')

        # remove task from queue
        tasks.popleft()


if __name__ == '__main__':
    # https://moviemosaic.org/user/shuval/d9a577be-2fef-4120-9a4a-ab464ff355b2
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS TASKS(id, user, mode, progress_msg, status, error_msg)")
    cur.execute("CREATE TABLE IF NOT EXISTS RESULTS(id, result, created_on)")
    cur.close()
    db.commit()
    main(db)