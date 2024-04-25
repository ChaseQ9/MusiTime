from flask import Flask, redirect, url_for, request, render_template
from main import *

app = Flask(__name__)

@app.route('/update', methods=['POST'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        sp = set_up(user)
        length = int(request.form['length'])
        long_to_short = bool(request.form['long_to_short'])
        recomendations = rec_ttracks_songs()
        songs = find_songs_in_length(recomendations, length, long_to_short)
        add_to_playlist(songs)
        return render_template('success.html')
    else:
        exit()

if __name__ == '__main__':
	app.run(debug=True, port=5002)
