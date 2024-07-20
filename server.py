import os
from dotenv import load_dotenv
if os.path.isfile('.env'):
    load_dotenv('.env')
from datetime import datetime
from fetch_data import scrape, rss_feed_exists, valid_movies, MovieCellBuilder, Scraper, Transformer
from image_builder import build
from ratio_tester import get_moviecells
from flask import Flask, redirect, url_for, request, session, send_file, render_template
import io
import base64
import secrets
from apscheduler.schedulers.background import BackgroundScheduler
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = secrets.token_urlsafe(16)
Session(app)

def validate_submitted_string(s: str) -> bool:
	# temporary until I figure out how i want to structure this
	return True and rss_feed_exists(s)

@app.route('/user/<string:username>')
def dynamic_page(username: str):
    image_string = create_mosaic(username)
    session[f'{username}_image_string'] = image_string
    download_url = url_for('download_image', username=username)
    return render_template('dynamic_page.html', image=image_string, download_url=download_url)

@app.route('/download/<string:username>')
def download_image(username: str):
    image_string = session.get(f'{username}_image_string', None)
    if not image_string:
        # user went directly to download page
        image_string = create_mosaic(username)
        session[f'{username}_image_string'] = image_string

    image_data = base64.b64decode(image_string)
    buffer = io.BytesIO(image_data)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f'{username}.png', mimetype='image/png/')


@app.route('/', methods=['GET', 'POST'])
def main_form():
    if request.method == 'GET':
        return render_template('main_form.html')
    
    submitted_username = request.form['username_submitted']
    movie_cell_builder = MovieCellBuilder(
        username=submitted_username,
        mode=0
    )
    status = movie_cell_builder.get_status()
    
    if not status[0]:
        return render_template('main_form.html', error_message=status[1])

    session[f'{submitted_username}_MovieCellBuilder'] = movie_cell_builder.to_dict()
    return redirect(url_for('dynamic_page', username=submitted_username))


def create_mosaic(username: str):
    mv_builder = rebuild_movie_builder(username=username)
    movie_cells = mv_builder.build_cells()

    # image_str is used for displaying image on webpage

    buffer = io.BytesIO()
    image = build(movie_cells, username, 'config.json')
    image.save(buffer, format='PNG')
    buffer.seek(0)
    image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_string

def rebuild_movie_builder(username: str) -> MovieCellBuilder:
    mv_builder_dict = session.get(f'{username}_MovieCellBuilder', None)

    if not mv_builder_dict:
        return None

    builder = MovieCellBuilder(
        username=mv_builder_dict['_username'],
        mode=mv_builder_dict['_mode'],
        status=mv_builder_dict['_status'],
        movie_data=mv_builder_dict['_movie_data']
    )

    return builder

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
