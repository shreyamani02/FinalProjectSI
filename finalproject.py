import json
import sys
import os
import matplotlib
import sqlite3
import csv
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import unittest
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials #To access authorised Spotify data
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

cid = '80e4d2a8c2734c8e882a74e6f2c3e9bd'
secret = '9a43668b2bcc4b02a047683c2226defc'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
name = "{Taylor Swift}"
result = sp.search(name)
#print(result['tracks']['items'][0]['artists'])
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

#Phoebe, Shreya, Isabelle


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def createTables(cur, conn):
    
    cur.execute("""CREATE TABLE IF NOT EXISTS 'Songs' 
        ('song_id' INTEGER PRIMARY KEY, 'song_title' TEXT, 'album_id' NUMBER, 
         'length' INTEGER, 'popularity' INTEGER, 'danceability' REAL, 'energy' REAL)""")
        #am i missing anything? are we doing ratings
    cur.execute("""CREATE TABLE IF NOT EXISTS "Albums" ('id' INTEGER PRIMARY KEY, 'album_title' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Music Videos" ('id' INTEGER PRIMARY KEY, 'song_title' NUMBER, 'views' INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Awards" ('id' INTEGER PRIMARY KEY, 'award_show_name' NUMBER, 'num_wins' INTEGER, 'num_noms' INTEGER)""")

    conn.commit()

def scrapeWiki(soup):
    wiki_dict = {}
    new_dict = {}
    iterator = 1
    key = ""
    for i in soup.findAll('table', class_ = 'collapsible collapsed'):
        for winsnoms in i.findAll('td'):
            if iterator == 1:
                key = winsnoms.text.strip()
                wiki_dict[key] = {}
                iterator = 2
            elif iterator == 2:
                new_dict['wins'] = winsnoms.text.strip()
                iterator = 3
            else:
                new_dict['noms'] = winsnoms.text.strip()
                wiki_dict[key] = new_dict
                new_dict = {}
                iterator = 1

    return wiki_dict

def spotifyApi():
    artist_uri = result['tracks']['items'][0]['artists'][0]['uri']
    sp_albums = sp.artist_albums(artist_uri, album_type='album')
    artist_data_list = []
    song_id_list = []
    print("printing album list:")
    album_list = []
    for i in range(len(sp_albums['items'])):
        new_dict = {}
        new_dict['Album Name'] = sp_albums['items'][i]['name']
        album_list.append(sp_albums['items'][i]['name'])
        new_dict['Album Url'] = sp_albums['items'][i]['uri']
        tracks = sp.album_tracks(new_dict['Album Url'])
        tracklist = []
        for n in range(len(tracks)):
            data_dict = {}
            data_dict["Song Name"] = tracks['items'][n]['name']
            data_dict["Song Track Number"] = tracks['items'][n]['track_number']
            data_dict["Song URL"] = tracks['items'][n]['uri']
            data_dict["Track ID"] = tracks['items'][n]['id']
            track_id = tracks['items'][n]['id']
            song_id_list.append(track_id)
            tracklist.append(data_dict)
        new_dict['Track Data'] = tracklist
        artist_data_list.append(new_dict)

    return song_id_list, album_list

def update_spotify_data(ids, cur, conn, album_list):
    track_list = []
    song_id = 0
    #update album table
    for i in range(len(album_list)):
        cur.execute("""INSERT OR IGNORE INTO Albums (id, album_title) VALUES (?, ?)""", 
        (i, album_list[i]))

    for id in ids:
        meta = sp.track(id)
        features = sp.audio_features(id)

        new_track_info = []
        #fetch track info
        name = meta['name']
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        cur.execute('SELECT id from Albums WHERE album_title = ?',([album]))
        album_id = int((cur.fetchone()[0]))

        release_date = meta['album']['release_date']
        length = int(meta['duration_ms'])
        popularity = int(meta['popularity'])
        danceability = float(features[0]['danceability'])
        energy = float(features[0]['energy'])
        new_track_info = [name, album, artist, release_date, length, popularity, danceability, energy]
        track_list.append(new_track_info)

        cur.execute(
            """INSERT OR IGNORE INTO Songs (song_id, song_title, album_id, length, popularity, danceability, energy)
                VALUES (?, ?, ?,  ?, ?, ?, ?)""",
                (song_id, name, album_id, length, popularity, danceability, energy)
        )
        song_id += 1
    conn.commit()


def youtubeAPI():
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyDxoKyMEt6S3NdpT_yOIFTkSK3yWxQGbaE"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = api_key)
    
    playlist = {"Red (Taylor's Version)": "OLAK5uy_lhEyrFap1OvMSwsL3AoZdrvqlRdJvyx0M",
                "Fearless (Taylor's Version)": "OLAK5uy_lUwH9j_s3ZEeayUSm5o93gtQVz0If_kd8",
                "Evermore":"OLAK5uy_m-vSVOiVeY_z2lPgThmS6Nn0TJExXZtOg",
                "Folklore":"OLAK5uy_nWgO-2lNMsx90439Yx0xTWCGIktUc74e8",
                "Lover":"OLAK5uy_nHHWc9S0Nw7oLyLYBptkJ4DpkQeoL1Igw",
                "Reputation": "OLAK5uy_kyYsExXByLh2281MMfi0QvZJF5epEUxbk",
                "1989":"OLAK5uy_lglIKPOFCG5X9_Rf4Hxsmmh9GEeHL94Jo",
                "Red (Delux Addition)": "OLAK5uy_mwwCV3ci_DoOhgq27DRqnrVG3QOR_S2hQ",
                "Speak Now": "OLAK5uy_k_sq8Sp6KDtHZIxW6ovITiJhl6SIC-5gw",
                "Fearless":"OLAK5uy_kymlVnEd_mmMQfc4GJJPTNOW-ipnOhsrY"
                }
    
    album_videos = {}
    
    for album in playlist.keys():
        request = youtube.playlistItems().list(
            part="contentDetails, snippet",
            playlistId=playlist[album],
            maxResults = 50
        )
        response = request.execute()
        
        song_list = []
        
        items = response["items"]
        for i in items:
            sub_it = i["snippet"]
            title = sub_it["title"]
            song_list.append((title))
        
        album_videos[album] = song_list
    
    return album_videos

def updateAPI (cur, conn, data):
    #update w wiki info
    id = 0
    for item in data:
        award_show_name = item['award_show_name'] #idk what this means w the integers
        num_noms = int(item['noms'])
        num_wins = int(item['wins'])
        cur.execute(
            """
            INSERT OR IGNORE INTO Awards (id, award_show_name, num_wins, num_noms) 
            VALUES (?, ?, ?, ?)
            """,
            (id, award_show_name, num_noms, num_wins)
        )
        id += 1
    conn.commit()


def avg_length_album(name, cur, conn):
    pass

def most_music_videos(cur, conn, data):
    pass

def avg_rating(cur, conn, album):
    pass

def write_calculations(data):
    pass

def avg_rating_graph(cur, conn, data):
    pass

def avg_length_graph(cur, conn, data):
    pass

def total_length_graph(cur, conn, data):
    pass

def pie_chart_genre(cur, conn, data):
    pass

def ratings_vs_rollingstone(cur, conn, data):
    pass

def main():
    url = "https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Taylor_Swift"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    #wiki_data = scrapeWiki(soup)
    spotify_data, albums = spotifyApi()

    cur, conn = setUpDatabase('db_vol_4.db')
    """
    cur.execute("DROP TABLE IF EXISTS Songs")
    cur.execute("DROP TABLE IF EXISTS Albums")
    cur.execute("DROP TABLE IF EXISTS Genres")
    """
    
    createTables(cur, conn)


    update_spotify_data(spotify_data, cur, conn, albums)
    #updateAPI(cur, conn, wiki_data)

main()
