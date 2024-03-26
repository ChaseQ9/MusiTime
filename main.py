
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
scope = ["playlist-modify-public", "playlist-modify-private", "user-top-read"]
user = input("Username for account: ")
def OAuth(): 
    token = util.prompt_for_user_token(username=user, scope=scope, client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET, redirect_uri=redirect_uri, cache_path=".cache")
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
def get_user_playlist() -> dict:
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

def get_song_duration(track: str) -> int:
    # can give info of track by ID or URL or URI
    trackInfo = sp.track(track)
    duration_ms = trackInfo["duration_ms"]
    total_seconds = duration_ms // 1_000        # total seconds is acquired here, everything below is extra (optional)
    # mins, secs = divmod(total_seconds, 60)
    # print("{:0>2}:{:0>2}".format(mins, secs))
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
    
    
def create_playlist() -> None:
    user_has = _user_has_playlist(user, "MusiTime")  
    if user_has is not None:
        _clear_playlist(user_has)
        print("Playlist wiped!")
        return
    else:
        sp.user_playlist_create(user=user, public=True, name="MusiTime", collaborative=False,description="Playlist made by MusiTime")
        print("Successfully created MusiTime Playlist!")
        return
    

def _user_has_playlist(user_id, playlist_name): # working
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']
    print("_user_has_playlist ends here...")
    return None

def _clear_playlist(playlist_id):   # working
    # Get all tracks in the playlist
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    # Iterate over each track and remove it from the playlist
    while tracks:
        for track in tracks:
            sp.playlist_remove_all_occurrences_of_items(playlist_id, [track['track']['id']])
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
    print("_clear_playlist ends here...")
        
        
def _get_OPTION(songs: list, OPTION: str) -> list: # function returns id's of songs in given playlist
    tracks = songs["items"]
    return_list = []
    for track in tracks:
        return_list.append(track[OPTION])
    print("_get_OPTION ends here...")
    return return_list

def add_to_playlist(songs: list) -> None: # always the MusiTime playlist; assumes list being passed is ID's 
    _clear_playlist(_user_has_playlist(user, "MusiTime"))
    sp.user_playlist_add_tracks(user=user,playlist_id=_user_has_playlist(user, "MusiTime"), tracks=songs, position=None)
    print("add_to_playlist ends here...")

def recommendations_func(choice: int) -> list: # NOT DONE
    if choice == 1: # doesnt break (but also doesnt return anythin rn)
        seed_genres = sp.recommendation_genre_seeds()
        recomendations = sp.recommendations(seed_genres=seed_genres, limit=100)
        recs = []
        for track in recomendations['tracks']:
            recs.append(track['id'])
        print("recommendations_func ends here...")
        return recs
    elif choice == 2: # doesnt work rn
        seed_artists = sp.current_user_top_artists(limit=5, time_range="long_term")
        recomendations = sp.recommendations(seed_artists=seed_artists, limit=100)
        recs = []
        for track in recomendations['tracks']:
            recs.append(track['id'])
        print("recommendations_func ends here...")
        return recs
    else: # works rn
        songs = sp.current_user_top_tracks(limit=5, time_range="long_term")
        songs = _get_OPTION(songs, "id")
        recomendations = sp.recommendations(seed_tracks=songs, limit=100)
        recs = []
        for track in recomendations['tracks']:
            print(track['name'])
            recs.append(track['id'])
        print("recommendations_func ends here...")
        return recs

sp = OAuth()

songs = sp.current_user_top_tracks(limit=5, time_range="long_term") # test functionality // Max limit is 50 top tracks
songs = _get_OPTION(songs, 'id')        # change songs into a list holding song ID's
recommendations = recommendations_func(3) # recommendation takes at most 5 seed tracks
add_to_playlist(recommendations)

    
