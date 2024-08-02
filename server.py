# ===========ENVIRONMENT=IMPORTS===========

import os
from dotenv import load_dotenv
if os.path.isfile('.env'):
    load_dotenv('.env')
if os.path.isfile('.env'):
    DATABASE = "./sqlitedata/database.sqlite3"
else:
    DATABASE = "/sqlitedata/database.sqlite3"
# =========================================

from datetime import datetime
from fetch_data import MovieCellBuilder
from image_builder import build
from ratio_tester import get_moviecells
from flask import Flask, redirect, url_for, request, session, send_file, render_template, g
import io
import base64
import secrets
from apscheduler.schedulers.background import BackgroundScheduler
from flask_session import Session
from bleach import clean
import sqlite3
from uuid import uuid4
import time

# setting up flask app
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = secrets.token_urlsafe(16)
Session(app)

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        cur = db.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS TASKS(id, user, mode, progress_msg, status, error_msg)")
        cur.execute("CREATE TABLE IF NOT EXISTS RESULTS(id, result, created_on)")
        cur.close()
        db.commit()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route('/download/<string:username>/<string:task_id>')
def download_image(username: str, task_id: str):

    image_string = get_result(task_id)
    if not image_string:
        redirect(url_for('main_form'))

    # render page with generated image_string
    image_data = base64.b64decode(image_string)
    buffer = io.BytesIO(image_data)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'{username}.png', mimetype='image/png/')

@app.route('/', methods=['GET', 'POST'])
def main_form():
    if request.method == 'GET':
        count_message = num_of_rows()
        return render_template('main_form.html', error_message=count_message)
    
    submitted_username = clean(request.form['username_submitted'])
    movie_mode = 0
    if request.form.get('movie_mode'):
        movie_mode = 1

    task_id = start_task(submitted_username, movie_mode)
    return redirect(url_for('task_page', task_id=task_id))

@app.route('/task/<string:task_id>')
def task_page(task_id: str):
    '''
    screen for displaying progress updates on the current task.
    task should be pushed to db before this is called.
    '''

    cur = get_db().cursor()
    cur.execute(f"""
    SELECT STATUS, PROGRESS_MSG, USER, ERROR_MSG FROM TASKS WHERE ID = ?
    """, (task_id,))

    task = cur.fetchone()
    cur.close()
    if task:
        status, progress_msg, username, error_msg = task

        if status == 'COMPLETE':
            # result has been pushed by worker
            # redirect to page to show user the image_string
            return redirect(url_for('dynamic_page', username=username, task_id=task_id))
        elif status == 'ERROR':
            return render_template('main_form.html', error_message=error_msg)

        # task still loading
        return render_template('task_page.html', progress_msg=progress_msg)
    else:
        return redirect(url_for('main_form', error_message=f'TASK: {task} | TASK_ID: {task_id}'))
    # serve an html page that uses the meta tag to refresh to display the current progress_msg

@app.route('/user/<string:username>/<string:task_id>')
def dynamic_page(username: str, task_id: str):
    '''
    displays image_string from RESULTS table in db after task complete
    '''
    image_string = get_result(task_id=task_id)
    if not image_string:
        redirect(url_for('main_form'))
    download_url = url_for('download_image', username=username, task_id=task_id)
    return render_template('dynamic_page.html', image=image_string, download_url=download_url)

def num_of_rows():
    cur = get_db().cursor()
    cur.execute("SELECT COUNT(*) FROM TASKS")
    cnt = cur.fetchone()
    cur.close()
    return str(cnt[0])

# TASKS(id, user, mode, progress_msg, status, error_msg)")
def start_task(user: str, mode: int) -> str:
    '''
    starts task in database and returns corresponding id of task
    '''

    task_id = str(uuid4())

    get_db().execute(
        """
        INSERT INTO TASKS 
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (task_id, user, mode, 'TASK QUEUED', 'READY', 'NULL')
    )
    get_db().commit()
    return task_id

def get_result(task_id: str) -> str:
    cur = get_db().cursor()
    cur.execute("""
    SELECT * FROM RESULTS WHERE ID = ?
    """, (task_id,))

    result_row = cur.fetchone()
    cur.close()

    if not result_row:
        return None

    id, result, time = result_row

    return result

def clear_data():
    '''Clear all data from TASKS and RESULTS tables.'''
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute("DROP TABLE IF EXISTS RESULTS;")
    cur.execute("DROP TABLE IF EXISTS TASKS;")
    cur.execute("CREATE TABLE TASKS(id TEXT PRIMARY KEY, user TEXT, mode INTEGER, progress_msg TEXT, status TEXT, error_msg TEXT)")
    cur.execute("CREATE TABLE RESULTS(id TEXT PRIMARY KEY, result TEXT, created_on TEXT)")
    db.commit()
    cur.close()
    db.close()

if __name__ == "__main__":
    # clear_data()
    app.run(host="0.0.0.0", port=8080, debug=True)

