
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from spotipy import util
from dotenv import load_dotenv
import os

load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8888/callback"

# set up a spotify class so that we can access user information
# uses client_id for the app and client_secret to connect

# OAuth Method for accessing Spotify Data (individual user accounts, browser verification required)
user = input("Username for account: ")
def OAuth(): 
    token = util.prompt_for_user_token(username=user, scope="playlist-modify-public", client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=redirect_uri, cache_path=".cache")
    sp = Spotify(auth=token)
    return sp
# Client Credential Method for accessing Spotify Data (any user accounts, no outside browser opened)
def ClientCred():
    sp = Spotify(auth_manager=SpotifyClientCredentials(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET))
    return sp

# to get username
# go to spotify.com --> account settings --> edit profile 
# spotify ID 

# TEST FUNCTION ::: ONLY WORKS WITH CLIENT_CREDS version of sp
# Function returns all playlists PUBLICLY accesible 
def get_user_playlist(sp) -> dict:
    user = input("Please enter Spotify username here: ")
    playlists = sp.user_playlists(user)
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return playlists

def get_song_duration(sp: Spotify, track: str) -> int:
    # can give info of track by ID or URL or URI
    trackInfo = sp.track(track)
    duration_ms = trackInfo["duration_ms"]
    total_seconds = duration_ms // 1_000        # total seconds is acquired here, everything below is extra (optional)
    mins, secs = divmod(total_seconds, 60)
    print("{:0>2}:{:0>2}".format(mins, secs))
    # print(total_seconds)
    return total_seconds

def get_length_of_playlist(playlist: dict) -> int:
    total = 0
    for item in playlist['tracks']['items']:
        # print(item['track']['id'])
        total += get_song_duration(sp, item['track']['id'])
    print(str(total) + " total seconds in the playlist, " + playlist['name'])
    
def is_valid(playlist_length: int, goal_length: int) -> bool:
        return playlist_length == goal_length
    
    
def create_playlist(songs_to_add: list) -> None:
        user_has = _user_has_playlist(user, "MusiTime")  
        if user_has is not None:
            _clear_playlist(user_has)
            print("Playlist wiped!")
            return
        else:
            sp.user_playlist_create(user=user, public=True, name="MusiTime", collaborative=False,description="Playlist made by MusiTime")
        print("Successfully created MusiTime Playlist!")

def _user_has_playlist(user_id, playlist_name):
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']
    return None

def _clear_playlist(playlist_id):
    # Get all tracks in the playlist
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    # Iterate over each track and remove it from the playlist
    while tracks:
        for track in tracks:
            sp.playlist_remove_all_occurrences_of_items(playlist_id, [track['track']['id']])
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        
sp = OAuth()

# results = sp.user_playlist("spotify", "https://open.spotify.com/playlist/37i9dQZF1DZ06evO1Exmrs?si=6793fc98a4d14e9c")
# get_length_of_playlist(results)
create_playlist([])

    