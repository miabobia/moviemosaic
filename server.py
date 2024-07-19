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
usernames = []

# def file_cleaner():
#     # this is executed every ten minutes
#     file_cleanup(usernames)

# scheduler = BackgroundScheduler()
# scheduler.add_job(file_cleaner, trigger='interval', minutes=10)
# scheduler.start()


def validate_submitted_string(s: str) -> bool:
	# temporary until I figure out how i want to structure this
	print(f'RSS FEED -> letterboxd.com/rss/{s}: {rss_feed_exists(s)}')
	return True and rss_feed_exists(s)

@app.route('/user/<string:username>')
def dynamic_page(username):
    usernames.append(username)
    image_string, image = create_mosaic(username)
    # session['image_path'] = file_saver(username=username, image=image)
    session[f'{username}_image_string'] = image_string
    download_url = url_for('download_image', username=username)
    # file_cleanup(filter_str=username)
    return render_template('dynamic_page.html', image=image_string, download_url=download_url)

@app.route('/download/<string:username>')
def download_image(username):
    # image_path = session.get('image_path', None)
    # image = read_image(image_path)
    image_string = session.get(f'{username}_image_string', None)
    if image_string:
        image_data = base64.b64decode(image_string)
        buffer = io.BytesIO(image_data)
        # buffer = io.BytesIO()
        # image_string.save(buffer, format='PNG')
        buffer.seek(0)
        # file_cleanup()
        return send_file(buffer, as_attachment=True, download_name=f'{username}.png', mimetype='image/png/')
    else:
        # generate image here if people want to directly dl image without visiting site?
        # redirect to dynamic page?
        return 'Image not found', 404

# FIGURE OUT SESSSIONS<>
# @app.after_request
# def after_request(response):
#     session.pop('error_message', None)
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     return response

@app.route('/', methods=['GET', 'POST'])
def main_form():
    if request.method == 'GET':
        return render_template('main_form.html')
    
    submitted_username = request.form['username_submitted']
    movie_cell_builder = MovieCellBuilder(
        username=submitted_username,
        mode=0,
        month=datetime.now().month
    )
    valid_username, error = movie_cell_builder.valid_username()

    session[f'{submitted_username}_MovieCellBuilder'] = movie_cell_builder.to_dict()

    # mv_builder = rebuild_movie_builder(submitted_username)
    
    if not valid_username:
        return render_template('main_form.html', error_message=error)

    # if not validate_submitted_string(submitted_username):
    #     return render_template('main_form.html', error_message='Invalid username')
    
    # movie_items = valid_movies(submitted_username, datetime.now().month)
    # if not movie_items:
    #     return render_template('main_form.html', error_message=f'No valid movies found for {submitted_username}')
    return redirect(url_for('dynamic_page', username=submitted_username))


def create_mosaic(username: str):
    # mv_builder_dict = session.get(f'{username}_MovieCellBuilder', None)

    # mv_builder = MovieCellBuilder(
    #     username=mv_builder_dict['_username'],
    #     mode=mv_builder_dict['_mode'],
    #     month=mv_builder_dict['_month']
    # )

    mv_builder = rebuild_movie_builder(username=username)
    movie_cells = mv_builder.build_cells()



    # image_str is used for displaying image on webpage
    # image is raw data of image. Save it to local storage
    # movie_cells = scrape(username, datetime.now().month)

    # if not movie_cells:
    #     return None, None

    image = build(movie_cells, username, 'config.json')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_string, image

def rebuild_movie_builder(username: str) -> MovieCellBuilder:
    mv_builder_dict = session.get(f'{username}_MovieCellBuilder', None)

    if not mv_builder_dict:
        movie_cell_builder = MovieCellBuilder(
            username=username,
            mode=0,
            month=datetime.now().month
        )
        session[f'{username}_MovieCellBuilder'] = movie_cell_builder.to_dict()
        return movie_cell_builder
    
    # if not '_scraper' in mv_builder_dict:
    #     return None
    
    # if not '_transformer' in mv_builder_dict:
    #     return None
    
    builder = MovieCellBuilder(
        username=mv_builder_dict['_username'],
        mode=mv_builder_dict['_mode'],
        month=mv_builder_dict['_month'],
        scraper=None,
        transformer=None
        # scraper=Scraper.from_dict(mv_builder_dict['_scraper']),
        # transformer=Transformer.from_dict(mv_builder_dict['_transformer'])
    )

    # builder._scraper = Scraper.from_dict(mv_builder_dict['_scraper'])
    # builder._transformer = Transformer.from_dict(mv_builder_dict['_transformer'])

    return builder
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)

# when i have post redirect using get
