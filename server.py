from datetime import datetime

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("getimage.html")

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
