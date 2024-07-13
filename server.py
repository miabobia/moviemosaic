from datetime import datetime
from fetch_data import scrape, rss_feed_exists
from time import time
from file_management import file_cleanup, file_saver, serve_image, read_image
from image_builder import build
from ratio_tester import get_moviecells
from flask import Flask, redirect, url_for, request, session, send_file, render_template
import io
import base64
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
IMAGES_DIRECTORY = './images'


def validate_submitted_string(s: str) -> bool:
	# temporary until I figure out how i want to structure this
	print(f'RSS FEED -> letterboxd.com/rss/{s}: {rss_feed_exists(s)}')
	return True and rss_feed_exists(s)

@app.route('/user/<string:username>')
def dynamic_page(username):
    image_string, image = create_mosaic(username)
    session['image_path'] = file_saver(username=username, image=image)
    download_url = url_for('download_image', username=username)
    # file_cleanup(filter_str=username)
    return render_template('dynamic_page.html', image=image_string, download_url=download_url)


@app.route('/download/<string:username>')
def download_image(username):
    image_path = session.get('image_path', None)
    image = read_image(image_path)
    if image:
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        # file_cleanup()
        return send_file(buffer, as_attachment=True, download_name=f'{username}.png', mimetype='image/png')
    else:
        return 'Image not found', 404

@app.route('/', methods=['GET', 'POST'])
def main_form():
    if request.method == 'POST':
        submitted_string = request.form['username_submitted']
        if validate_submitted_string(submitted_string):
            return redirect(url_for('dynamic_page', username=submitted_string))

        else:
            error_message = 'Invalid submitted string'
            return render_template('main_form.html', error_message=error_message)
    return render_template('main_form.html')

def create_mosaic(username: str) -> str:
    # image_str is used for displaying image on webpage
    # image is raw data of image. Save it to local storage
    movie_cells = scrape(username, datetime.now().month)
    image = build(movie_cells, username, 'config.json')
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    image_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return image_string, image

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
