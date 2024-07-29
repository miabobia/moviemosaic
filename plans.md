
# the **plan**

decouple my code

# problem
currently there is one process  started from 'server.py'
this process handles:
- front end (serving up html, taking user input, handling sessions)
- back end (collecting data on user, downloading images, building images)
as my connection is kind of slow currently. wifi on raspberry pi in basement when router is two floors up :c operations are slow. downloading many movie posters for an image takes quite a while. building an image takes some time as well. 

why is this an issue?
when a user requests a movie mosaic it looks like the website is freezing and it hangs for over 5 seconds. 
# how do we fix it?
implementing a database

implementing a worker process

# how will the database integrate into codebase?
the database will be the 'communication layer' (probably wrong terminology but makes sense to me) between the front-end/back-end and the worker process.

# workflow
1. front-end takes in user input
2. front-end asks back-end to start a task
3. back-end inserts a new task into TASKS table in db 

| TASK      | ACTION                              | PROGRESS_MSG    | STATUS      | ERROR_MSG |
| --------- | ----------------------------------- | --------------- | ----------- | --------- |
| 883921839 | {letterboxd_username}_create_mosaic | COLLECTING DATA | IN PROGRESS | NULL      |
4. worker sees there is a new task in TASKS
5. worker starts ACTION
6. front-end displays PROGRESS_MSG to users on webpage. using constant meta-tag refresh for realtime updates
7. worker finishes action then inserts data into RESULTS table. possibly more actions but here's an example of a create_mosaic action

| TASK      | RESULT              |
| --------- | ------------------- |
| 883921839 | {image_byte_string} |
8. if the STATUS becomes ERROR then url redirects to homepage with ERROR_MSG. Otherwise once STATUS == COMPLETE then we redirect to /user/{letterboxd_username} with the image_byte_string from RESULT


# POSSIBLE ISSUES ?
does worker need threads to work on multiple tasks at once?


# EXAMPLE CODE
defined tables earlier like this
```
cursor.execute("CREATE TABLE tasks(id, action, progress_msg, status, error_msg)")
cursor.execute("CREATE TABLE results(id, result)")
```

front.py
```
from time import sleep
import sqlite3
import uuid

con = sqlite3.connect('mydb.db')
usernames = ['john', 'mia', 'targus', 'chris', 'chadley', 'derek', 'yama', 'lise', 'tunnelman', 'pilot']
i = 0
cursor = con.cursor()
while True:
    x = input('what u wanna do?')

    if str(x) != 't' and str(x) != 'd':
        # start task
        continue

    if str(x) == 'd':
        cursor.execute("SELECT * FROM TASKS")
        # print(cursor.fetchall())
        for row in cursor.fetchall():
            print(row,end='\n')

        continue

    cursor.execute(f'''INSERT INTO TASKS(id, action, progress_msg, status, error_msg)
                VALUES (?, ?, ?, ?, ?);''', (str(uuid.uuid4()), f'{usernames[i]}_create_mosaic', 'NOT STARTED', 'WAITING', 'NULL'))
    con.commit()
    i += 1
    if i == len(usernames): i = 0
```

worker.py
```
from time import sleep
import sqlite3
con = sqlite3.connect('mydb.db')

cursor = con.cursor()

statuses = ["WAITING", "PROGRESSING", "COMPLETE"]

task_check_query = "SELECT * FROM TASKS;"
while True:

    sleep(1)
    input('step')
    cursor.execute(task_check_query)

    rows = cursor.fetchall()

    for row in rows:
        print(row)
        if row[3] == "WAITING":
            cursor.execute(
                """
                UPDATE TASKS
                SET STATUS = "PROGRESSING"
                """
            )
            con.commit()
        elif row[3] == "PROGRESSING":
            cursor.execute(
                """
                UPDATE TASKS
                SET STATUS = "COMPLETE"
                """)
        elif row[3] == "COMPLETE":
            cursor.execute("""
                INSERT INTO RESULTS(id, result)
                VALUES (?, ?)
                           """, (row[0], 'TEST RESULT'))
        con.commit()

```

front.py in production wouldn't be on a while loop it would be constantly run via flask's event loop. 
Then we could constantly be checking the results table and tasks table to provide progress updates.
```input('step')``` was placed there just so i could test in real time since tasks would be done too quickly in this env
