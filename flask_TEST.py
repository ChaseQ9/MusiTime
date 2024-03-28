from flask import Flask, redirect, url_for, request, render_template
from main import *

app = Flask(__name__)


@app.route('/success/<name>')
def success(name):
	return f"Success! {name} MusiTime Playlist has been successfully updated"


@app.route('/update', methods=['POST'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        sp = set_up(user)
        recomendations = recommendations_func(3)
        add_to_playlist(recomendations)
        return render_template('success.html')
    else:
        exit()

if __name__ == '__main__':
	app.run(debug=True, port=5002)
