
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from spotipy import util
from dotenv import load_dotenv
import os
from utils import Song

load_dotenv()
SPOTIPY_CLIENT_ID = os.getenv("CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
redirect_uri = "http://localhost:8888/callback"
OFFSET = 120 # this offset is what is used in the determining songs to add to playlist

# set up a spotify class so that we can access user information
# uses client_id for the app and client_secret to connect

# OAuth Method for accessing Spotify Data (individual user accounts, browser verification required)
scope = ["playlist-modify-public", "playlist-modify-private", "user-top-read", "playlist-read-private", "user-library-read"]
def OAuth(user: str):     
    global sp
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

# 04/17/24 -- Works
def get_song_duration(track: str) -> int:
    # can give info of track by ID or URL or URI
    trackInfo = sp.track(track)
    duration_ms = trackInfo["duration_ms"]
    total_seconds = duration_ms // 1_000        # total seconds is acquired here, everything below is extra (optional)
    # mins, secs = divmod(total_seconds, 60)
    # print("{:0>2}:{:0>2}".format(mins, secs))
    # print(total_seconds)
    return total_seconds

# 04/17/24 -- Works
def get_length_of_playlist(playlist_id) -> int: # accuratley working 
    total = 0
    playlist = sp.playlist(playlist_id)
    for item in playlist['tracks']['items']:
        # print(item['track']['id'])
        total += get_song_duration(item['track']['id'])
    # print(str(total) + " total seconds in the playlist, " + playlist['name'])
    return total
# ON A TEST RUN
# get_length_playlist returned the correct seconds in the playlist offset by ~3 minutes
# we can implement a "grace offset" which allows our program to be off by a given time (EX: 5 Minutes)

# 04/17/24 -- Not Tested
def is_valid(playlist_length: int, goal_length: int) -> bool:
        return playlist_length == goal_length
    
# 04/17/24 -- Not Tested  
def create_playlist() -> None:
    user_has = _user_has_playlist(user, "MusiTime")  
    if user_has is not None:
        _clear_playlist(user_has)
        # print("Playlist wiped!")
        return
    else:
        sp.user_playlist_create(user=user, public=True, name="MusiTime", collaborative=False,description="Playlist made by MusiTime")
        # print("Successfully created MusiTime Playlist!")
        return
    
# 04/17/24 -- Works
def _user_has_playlist(user_id, playlist_name): # working
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            return playlist['id']
    # print("_user_has_playlist ends here...")
    return 
# 04/17/24 -- Works
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
    # print("_clear_playlist ends here...")
        
# 04/17/24 -- Works        
def _get_OPTION(songs: list, OPTION: str) -> list: # function returns id's of songs in given playlist
    tracks = songs["items"]
    return_list = []
    for track in tracks:
        return_list.append(track[OPTION])
    # print("_get_OPTION ends here...")
    return return_list
# 04/17/24 -- Works
def add_to_playlist(songs: list) -> None: # always the MusiTime playlist; assumes list being passed is ID's 
    # _clear_playlist(_user_has_playlist(user, "MusiTime"))
    create_playlist()
    sp.user_playlist_add_tracks(user=user,playlist_id=_user_has_playlist(user, "MusiTime"), tracks=songs, position=None)
    # print("add_to_playlist ends here...")



def get_artist_id(artists):
    artist_ids = []
    for artist in artists:
        search_results = sp.search(q="artist:" + artist, type='artist')
        if 'artists' in search_results and 'items' in search_results['artists']:
            for item in search_results['artists']['items']:
                if (len(artist_ids) < 5):
                    artist_ids.append(item['id'])
    return artist_ids
# 04/17/24 -- Working
def rec_artists_songs(artists: list) -> list:
    artists = get_artist_id(artists)
    recommendations = sp.recommendations(seed_artists=artists, limit=100)
    recs = []
    for track in recommendations['tracks']:
        recs.append(track['id'])
    # print("rec_artists_songs ends here...")
    return recs
# 04/17/24 -- Works
def rec_genre_songs(genres: list) -> list:
    recommendations = sp.recommendations(seed_genres=genres, limit=100)
    recs = []
    for track in recommendations['tracks']:
        recs.append(track['id'])
    # print("rec_genre_songs ends here...")
    return recs
# 04/17/24 -- Working
def rec_ttracks_songs() -> list:        # recommends top tracks
    songs = sp.current_user_top_tracks(limit=5, time_range="long_term")
    songs = _get_OPTION(songs, "id")
    recomendations = sp.recommendations(seed_tracks=songs, limit=100)
    recs = []
    for track in recomendations['tracks']:
        # print(track['name'])
        recs.append(track['id'])
    # print("rec_songs ends here...")
    return recs
    
# 04/17/24 -- works-ish; not perfect, not bad
# THIS IS WHERE THE ALGORITHM IS NEEDED
def find_songs_in_length(recs: list, goal_length: int, long_to_short: bool = None) -> list:
    if goal_length <= 0:                # EDGE CASE: user provides length less than or equal to 0
        return ["43JK3XJKQ5MJ7ddlF0ylUX"]
    if goal_length > 300:               # EDGE CASE: user wants a playlist longer than we can provide
        goal_length = 300
    goal_length *= 60           # increase goal_length to account for seconds rather than minutes (EX: 20 minutes = 1200 seconds)
    
    total_length = 0
    song_to_add = []
    
    # changing here now
    songs = []
    for song in recs:
        songs.append(Song(get_song_duration(song), song))
    # song.time and song.id hold respective songs id and time
    # we can use this to call quicksort on the associated times 
    # and use the ids as the songs we are going to return back to the program
    
    def quicksort(arr, rev: bool): # sort the songs
        if len(arr) <= 1:
            return arr
        else:
            pivot = arr[0]
            left = [x for x in arr[1:] if x.time < pivot.time]
            right = [x for x in arr[1:] if x.time >= pivot.time]
            if rev:
                return quicksort(right, rev) + [pivot] + quicksort(left, rev)
            else:
                return quicksort(left, rev) + [pivot] + quicksort(right, rev)
    if long_to_short is not None:       # if long_to_short is None, it acts as a "dont care" order of the playlist
        songs = quicksort(songs, long_to_short)
    for song in songs:
        if song.time + total_length <= goal_length + OFFSET:
            total_length += song.time 
            song_to_add.append(song.id)
    return song_to_add

    
    
    return song_to_add
# 04/17/24 -- Works
def set_up(username: str): # FOR USAGE WITH: flask_TEST.py
    global sp
    global user
    user = username
    return OAuth(user=user)

# 04/17/24 -- Works
def main():                 # FOR USAGE WITH: main.py; DRIVER CODE to TEST functions
    global user
    user = "chasequigley9"
    sp=OAuth(user=user)
    recs = rec_ttracks_songs()
    # recs = rec_genre_songs(["pop", "country", "hip-hop"])
    # recs = rec_artists_songs(['Morgan Wallen', 'Juice WRLD', 'Zach Bryan'])
    # get_artist_id(['Morgan Wallen', 'Juice WRLD', 'Zach Bryan'])
    songs = find_songs_in_length(recs, 300)
    add_to_playlist(songs)
if __name__ == '__main__':
    main()
