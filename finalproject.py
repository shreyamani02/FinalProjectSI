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
<<<<<<< HEAD
=======

>>>>>>> b3b2544d6de4c9d805aa6ddc7c36add972a6f0e4

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
<<<<<<< HEAD
    
    cur.execute("""CREATE TABLE IF NOT EXISTS 'Songs' 
        ('song_id' INTEGER PRIMARY KEY, 'song_title' TEXT, 'album_id' NUMBER, 
         'length' INTEGER, 'popularity' INTEGER, 'danceability' REAL, 'energy' REAL)""")
        #am i missing anything? are we doing ratings
    cur.execute("""CREATE TABLE IF NOT EXISTS "Albums" ('id' INTEGER PRIMARY KEY, 'album_title' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Music Videos" ('id' INTEGER PRIMARY KEY, 'song_title' NUMBER, 'views' INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Awards" ('id' INTEGER PRIMARY KEY, 'award_show_name' NUMBER, 'num_wins' INTEGER, 'num_noms' INTEGER)""")

    conn.commit()
=======
    #songs (title, album #, artist/collaborator #, song length, genre #, )
    #album ()
    #genre ()
    #awards?
    #music video (title, length, views, ?)
    cur.execute("DROP TABLE IF EXISTS Awards")
    cur.execute("DROP TABLE IF EXISTS Music_Videos")
    cur.execute("DROP TABLE IF EXISTS Songs")

    cur.execute("""CREATE TABLE IF NOT EXISTS 'Songs' 
        ('song_id' INTEGER PRIMARY KEY, 'song_title' TEXT, 'album_id' NUMBER, 
         'length' INTEGER, 'genre_id' NUMBER, 'popularity' INTEGER, 'danceability' REAL, 'energy' REAL)""")
        #am i missing anything? are we doing ratings
    cur.execute("""CREATE TABLE IF NOT EXISTS "Albums" ('id' INTEGER PRIMARY KEY, 'album_title' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Genres" ('id' INTEGER PRIMARY KEY, 'genre_name' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Music_Videos" ('id' INTEGER PRIMARY KEY, 'song_title' NUMBER, 'song_name' TEXT, 'album_name' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Awards" ('id' INTEGER PRIMARY KEY, 'award_show_name' NUMBER, 'num_wins' INTEGER, 'num_noms' INTEGER)""")
>>>>>>> b3b2544d6de4c9d805aa6ddc7c36add972a6f0e4

    conn.commit()

def scrapeWiki(soup, cur, conn):
    wiki_dict = {}
    new_dict = {}
    iterator = 1
    award_id = 0
    key = ""
    for i in soup.findAll('table', class_ = 'collapsible collapsed'):
        for winsnoms in i.findAll('td'):
            if iterator == 1:
                key = winsnoms.text.strip()
                wiki_dict[key] = {}
                iterator = 2
            elif iterator == 2:
                try:
                    new_dict['wins'] = int(winsnoms.text.strip())
                except:
                    new_dict['wins'] = winsnoms.text.strip()
                iterator = 3
            else:
                try:
                    new_dict['noms'] = int(winsnoms.text.strip())
                except:
                    new_dict['noms'] = winsnoms.text.strip()
                wiki_dict[key] = new_dict
                new_dict = {}
                iterator = 1
<<<<<<< HEAD

=======
    del wiki_dict['Totals']
    for winsnoms in wiki_dict:
        cur.execute(
            """INSERT OR IGNORE INTO Awards (id, award_show_name, num_wins, num_noms)
            VALUES (?, ?, ?, ?)""",
            (award_id, winsnoms, wiki_dict[winsnoms]['wins'], wiki_dict[winsnoms]['noms'])
        )
        award_id += 1
    conn.commit()
>>>>>>> b3b2544d6de4c9d805aa6ddc7c36add972a6f0e4
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
<<<<<<< HEAD
        artist_data_list.append(new_dict)

    return song_id_list, album_list

def playlist_data():
    offset = 0
    pl_id = 'spotify:playlist:4GtQVhGjAwcHFz82UKy3Ca'
    big_list = []
    while True:
        response = sp.playlist_items(pl_id,
                                 offset=offset,
                                 fields='items,total',
                                 additional_types=['track'])
       
        if len(response['items']) == 0:
            break
       
 
        big_list.append(response['items'])
        offset = offset + len(response['items'])
 
        #print(offset, "/", response['total'])
   
   
    ids = []
    test_dict = []
    albums = []
    for list in big_list:
        for dict in list:
            #print(dict.keys())
            test_dict.append(dict['track']['album']['name'])
            ids.append(dict['track']['id'])
            album = dict['track']['album']['name']
            if album not in albums:
                albums.append(dict['track']['album']['name'])
 
            #for key in dict['track']:
            #    print(key)
   
 
    return ids, albums
    #known- there are 3 pages of data to pull


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
=======
        artist_data_list.append(new_dict) 
    return artist_data_list
>>>>>>> b3b2544d6de4c9d805aa6ddc7c36add972a6f0e4

def update_spotify_data(cur, conn):
    track_list = []
    id = 0
    song_id = 0
    track_no = 1
    album_name = "Red (Taylor's Version)"

<<<<<<< HEAD
def youtubeAPI():
=======
    ids = []
    artist_uri = result['tracks']['items'][0]['artists'][0]['uri']
    sp_albums = sp.artist_albums(artist_uri, album_type='album')
    for i in range(len(sp_albums['items'])):
        album_url = sp_albums['items'][i]['uri']
        tracks = sp.album_tracks(album_url)
        for n in range(len(tracks)):
            track_id = tracks['items'][n]['id']
            ids.append(track_id)

    for id in ids:
        meta = sp.track(id)
        features = sp.audio_features(id)

        new_track_info = []
        #fetch track info
        name = meta['name']
        name = name.lower()
        album = meta['album']['name']
        artist = meta['album']['artists'][0]['name']
        release_date = meta['album']['release_date']
        length = meta['duration_ms']
        popularity = meta['popularity']
        danceability = features[0]['danceability']
        energy = features[0]['energy']
        new_track_info = [name, track_no, album, artist, release_date, length, popularity, danceability, energy]
        if album_name == album:
            track_no += 1
        else: 
            album_name = album
            track_no = 1
        track_list.append(new_track_info)
        cur.execute(
            """INSERT OR IGNORE INTO Songs (song_id, song_title, album_id, length, genre_id, popularity, danceability, energy)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (song_id, name, 0, length, 0, popularity, danceability, energy)
        )
        song_id += 1
    conn.commit()
    return track_list

def get_song_ids(cur, conn):
    cur.execute(
        """
        SELECT Songs.song_id
        FROM Music_Videos JOIN Songs
        Where Music_Videos.song_name = songs.song_title 
        """
    )
    song_ids = cur.fetchall()
    conn.commit()
    return song_ids

def youtubeAPI(cur, conn):
>>>>>>> b3b2544d6de4c9d805aa6ddc7c36add972a6f0e4
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
<<<<<<< HEAD
    
=======
    song_id = 0
    album_id = 0
    track_iterator = 0
    for video in album_videos:
        for song in album_videos[video]:
            cur.execute(
                """INSERT OR IGNORE INTO Music_Videos (id, song_title, song_name, album_name)
                VALUES (?, ?, ?, ?)""",
                (song_id, 0, song.lower(), album_id)
            )
            track_iterator += 1
            song_id += 1 
        album_id+= 1
    track_ids = get_song_ids(cur, conn)
    conn.commit()
    print("TRACK ID")
    print(track_ids)
    conn.commit()
>>>>>>> b3b2544d6de4c9d805aa6ddc7c36add972a6f0e4
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


def avg_winsnoms_ratio(cur, conn):
    sum_ratio = 0
    count = 0
    cur.execute("""
    SELECT num_wins, num_noms
    FROM Awards
    """)
    res = cur.fetchall()
    for award in res:
        count += 1
        wins = award[0]
        noms = award[1]
        sum_ratio += float(wins/noms)
    avg_ratio = sum_ratio / count
    print("The average ratio of wins to nominations that Taylor Swift has achieved at award shows is ", avg_ratio)
    conn.commit()
    return avg_ratio



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
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.text, 'html.parser')
<<<<<<< HEAD
    #wiki_data = scrapeWiki(soup)
    ids, albums = playlist_data()
=======
    cur, conn = setUpDatabase('db_vol_4.db')
    createTables(cur, conn)
    scrapeWiki(soup, cur, conn)
    avg_winsnoms_ratio(cur, conn)
    spotifyApi()
    youtubeAPI2 = youtubeAPI(cur, conn)
    print(youtubeAPI2)
    print(update_spotify_data(cur, conn))

>>>>>>> b3b2544d6de4c9d805aa6ddc7c36add972a6f0e4

    cur, conn = setUpDatabase('db_vol_4.db')
    """
    cur.execute("DROP TABLE IF EXISTS Songs")
    cur.execute("DROP TABLE IF EXISTS Albums")
    cur.execute("DROP TABLE IF EXISTS Genres")
    """
    
    createTables(cur, conn)


    update_spotify_data(ids, cur, conn, albums)
    #updateAPI(cur, conn, wiki_data)

main()
