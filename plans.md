
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

