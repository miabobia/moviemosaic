import os
from dotenv import load_dotenv
if os.path.isfile('.env'):
    load_dotenv('.env')
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

# ===============================================

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = secrets.token_urlsafe(16)
Session(app)

DATABASE = "/sqlitedata/database.sqlite3"

# ===============================================

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # create table if it does not exist
        db.execute("create table if not exists hits (x int)")
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route('/user/<string:username>')
# @profile_function('dynamic_page_profile.pstat')
def dynamic_page(username: str):

    username = clean(username)

    # see if serving image to user is possible
    movie_cell_builder_dict = session.get(f'{username}_MovieCellBuilder', None)
    movie_cell_builder: MovieCellBuilder
    if not movie_cell_builder_dict:
        # this means user went directly to this page instead of through homepage
        movie_cell_builder = create_movie_cell_builder(username=username)
    else:
        movie_cell_builder = rebuild_movie_cell_builder(username=username)

    # movie_cell_builder exists now
    # check the state
    status, err = movie_cell_builder.get_status()
    if not status:
        # data from username is no good so we go back to homepage with error message
        return render_template('main_form.html', error_message=err)
    else:
        # put movie_cell_builder in session (could be overwriting duplicate data if session was already good)
        session[f'{username}_MovieCellBuilder'] = movie_cell_builder.to_dict()

    # username is viable so we load image_string into session
    create_mosaic(username=username)

    # render page with generated image_string
    image_string = session.get(f'{username}_image_string')
    download_url = url_for('download_image', username=username)
    return render_template('dynamic_page.html', image=image_string, download_url=download_url)

@app.route('/download/<string:username>')
def download_image(username: str):
    username = clean(username)
    # see if serving image to user is possible




    movie_cell_builder_dict = session.get(f'{username}_MovieCellBuilder', None)
    movie_cell_builder: MovieCellBuilder
    if not movie_cell_builder_dict:
        # this means user went directly to this page instead of through homepage
        movie_cell_builder = create_movie_cell_builder(username=username)
    else:
        movie_cell_builder = rebuild_movie_cell_builder(username=username)

    # movie_cell_builder exists now
    # check the state
    status, err = movie_cell_builder.get_status()
    if not status:
        # data from username is no good so we go back to homepage with error message
        return render_template('main_form.html', error_message=err)
    else:
        # put movie_cell_builder in session (could be overwriting duplicate data if session was already good)
        session[f'{username}_MovieCellBuilder'] = movie_cell_builder.to_dict()

    # username is viable so we load image_string into session
    create_mosaic(username=username)

    # render page with generated image_string
    image_string = session.get(f'{username}_image_string')
    image_data = base64.b64decode(image_string)
    buffer = io.BytesIO(image_data)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'{username}.png', mimetype='image/png/')


@app.route('/', methods=['GET', 'POST'])
# @profile_function('main_form.pstat')
def main_form():
    if request.method == 'GET':
        return render_template('main_form.html')
    
    submitted_username = clean(request.form['username_submitted'])
    movie_mode = 0
    if request.form.get('movie_mode'):
        movie_mode = 1

    # make sure session is cleared if image generation settings changed

    if session.get(f'{submitted_username}_MovieCellBuilder', None):
        # compare changes to current front page settings
        movie_dict = session.get(f'{submitted_username}_MovieCellBuilder')
        if movie_dict['_mode'] != movie_mode:
            session.pop(f'{submitted_username}_MovieCellBuilder')
            session.pop(f'{submitted_username}_image_string')

    movie_cell_builder = create_movie_cell_builder(username=submitted_username, mode=movie_mode)
    session[f'{submitted_username}_MovieCellBuilder'] = movie_cell_builder.to_dict()
    status, err = get_movie_cell_builder_status(movie_cell_builder)
    if request.form.get('movie_mode'):
        print(f'movie_mode: {request.form.get('movie_mode')}')
    if not status:
        return render_template('main_form.html', error_message=err)

    return redirect(url_for('dynamic_page', username=submitted_username))

# @profile_function('create_mosaic.pstat')
def create_mosaic(username: str):
    '''
    Pushes Movie Mosaic image based on username into session.
    Only called if viable movie_cell_builder in session.
    '''

    if session.get(f'{username}_image_string', None):
        return

    mv_builder = rebuild_movie_cell_builder(username=username)
    movie_cells = mv_builder.build_cells()
    last_watched_date = mv_builder.get_last_movie_date()

    buffer = io.BytesIO()
    image = build(movie_cells, username, 'config.json', last_watch_date=last_watched_date)
    image.save(buffer, format='PNG')
    buffer.seek(0)
    image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    session[f'{username}_image_string'] = image_string

# @profile_function('create_movie_cell_builder.pstat')
def create_movie_cell_builder(username: str, mode: int = 0) -> MovieCellBuilder:
    return MovieCellBuilder(
        username=username,
        mode=mode
    )
def get_movie_cell_builder_status(movie_cell_builder: MovieCellBuilder) -> tuple[bool, str]:
    return movie_cell_builder.get_status()

# @profile_function('rebuild.pstat')
def rebuild_movie_cell_builder(username: str) -> MovieCellBuilder:
    '''
    Takes in username and builds MovieCellBuilder based on current session.
    Only call when movie_cell_bulider exists in session!!
    '''
    mv_builder_dict = session.get(f'{username}_MovieCellBuilder', None)

    builder = MovieCellBuilder(
        username=mv_builder_dict['_username'],
        mode=mv_builder_dict['_mode'],
        status=mv_builder_dict['_status'],
        movie_data=mv_builder_dict['_movie_data']
    )
    return builder

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

