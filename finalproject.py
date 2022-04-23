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
print(result['tracks']['items'][0]['artists'])

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

#Phoebe, Shreya, Isabelle


def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def createTables(cur, conn):
    #songs (title, album #, artist/collaborator #, song length, genre #, )
    #album ()
    #collaborators ()
    #genre ()
    #awards?
    #music video (title, length, views, ?)
    cur.execute("""CREATE TABLE IF NOT EXISTS 'Songs' 
        ('song_id' INTEGER PRIMARY KEY, 'song_title' TEXT, 'album_id' NUMBER, 
        'collab_id' NUMBER, 'length' INTEGER, 'genre_id' NUMBER)""")
        #am i missing anything? are we doing ratings
    cur.execute("""CREATE TABLE IF NOT EXISTS "Albums" ('id' INTEGER PRIMARY KEY, 'album_title' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Artists" ('id' INTEGER PRIMARY KEY, 'artist_name' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Genres" ('id' INTEGER PRIMARY KEY, 'genre_name' TEXT)""")
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
    for i in range(len(sp_albums['items'])):
        new_dict = {}
        new_dict['Album Name'] = sp_albums['items'][i]['name']
        new_dict['Album Url'] = sp_albums['items'][i]['uri']
        tracks = sp.album_tracks(new_dict['Album Url'])
        tracklist = []
        for n in range(len(tracks)):
            data_dict = {}
            data_dict["Song Name"] = tracks['items'][n]['name']
            data_dict["Song Track Number"] = tracks['items'][n]['track_number']
            data_dict["Song URL"] = tracks['items'][n]['uri']
            data_dict["Track ID"] = tracks['items'][n]['id']
            tracklist.append(data_dict)
        new_dict['Track Data'] = tracklist
        artist_data_list.append(new_dict)
    print(artist_data_list)


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
    pass

def avg_length_album(name, cur, conn):
    pass

def most_music_videos(cur, conn, data):
    pass

def avg_rating(cur, conn, album):
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
    scrapeWiki(soup)
    spotifyApi()
    album_video_dict = youtubeAPI()

    cur, conn = setUpDatabase('new_db.db')
    createTables(cur, conn)

main()

