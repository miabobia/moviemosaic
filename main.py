from datetime import datetime
from fetch_data import scrape
from time import time
from file_management import file_cleanup, file_saver
from image_builder import build
from ratio_tester import get_moviecells
from flask import Flask, redirect, url_for, request, make_response, send_file
import os

app = Flask(__name__)
IMAGES_DIRECTORY = './images'

# @app.route('/fetch/<filename>', methods=['GET', 'POST'])
def return_mosaic(filename: str):
	print('return mosaic started')
	try:
		file_path = os.path.join(IMAGES_DIRECTORY, filename)
		print(f'OS FILE PATH: {file_path}')
		if os.path.isfile(file_path):
			return send_file(file_path, as_attachment=True)
		else:
			return make_response(f'File {filename} not found.', 404)
	except Exception as e:
		return make_response(f'Error: {str(e)}'), 500
	


@app.route('/getimage', methods=['POST', 'GET'])
def homepage():
	if request.method == 'POST':
		username = request.form['nm']
		try:
			movie_cells = scrape(username, datetime.now().month)
		except Exception("ERROR: Username does not exist"):
			print('EXCEPTING')
			return make_response(f'Username {username} does not exist.', 404)
		

		image = build(movie_cells, username, 'config.json')
		file_path = file_saver(username, image)
		return return_mosaic(file_path)
	else:
		username = request.form['nm']
		image = build(scrape(username, datetime.now().month), username, 'config.json')
		file_path = file_saver(username, image)
		return return_mosaic(file_path)
		return redirect(url_for(f'fetch', filename=file_path))
# def get_image():
# 	username = 'scooterwhiskey'
# 	return build(scrape(username, datetime.now().month), username, 'config.json')


if __name__ == '__main__':
	# image_path = 'images/705221-furiosa-a-mad-max-saga-0-1000-0-1500-crop.jpg'
	t0 = time()
	# username = 'scooterwhiskey'
	# cells = scrape(username, datetime.now().month)

	# for cell in cells:
	# 	print(vars(cell))

	# replace cells with get_moviecells(n) for testing with dummy data
	# build(cells, username, 'config.json').show()
	
	app.run(debug=True)
	# delete stored files
	file_cleanup()
	t1 = time()

	print(f'PROGRAM FINISHED IN {t1-t0}')
		