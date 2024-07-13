from datetime import datetime
from fetch_data import scrape
from time import time
from file_management import file_cleanup, file_saver, get_file_data
from image_builder import build
from ratio_tester import get_moviecells
from flask import Flask, redirect, url_for, request, make_response, send_file, render_template
import os
from requests import request

app = Flask(__name__)
IMAGES_DIRECTORY = './images'


def validate_submitted_string(s: str) -> bool:
	# temporary until I figure out how i want to structure this
	return True

@app.route('/user/<string:username>')
def dynamic_page(username):
    image, image_path = create_mosaic(username)  # You need to implement this function
    return render_template('dynamic_page.html', image=image, image_path=image_path)

@app.route('/', methods=['GET', 'POST'])
def main_form():
    if request.method == 'POST':
        submitted_string = request.form['username_submitted']
        if validate_submitted_string(submitted_string):  # You need to implement this function
            return redirect(url_for('dynamic_page', username=submitted_string))

        else:
            error_message = 'Invalid submitted string'
            return render_template('main_form.html', error_message=error_message)
    return render_template('main_form.html')

def create_mosaic(username: str) -> str:
	movie_cells = scrape(username, datetime.now().month)
	image = build(movie_cells, username, 'config.json')
	path = file_saver(username, image)
	return image, path

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
