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
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials #To access authorised Spotify data
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

cid = '80e4d2a8c2734c8e882a74e6f2c3e9bd'
secret = '9a43668b2bcc4b02a047683c2226defc'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
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
    cur.execute("""CREATE TABLE IF NOT EXISTS "Albums" ('id' INTEGER PRIMARY KEY, 'album_title' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Music_Videos" ('id' AUTO_INCREMENT INTEGER PRIMARY KEY, 'title' TEXT, 'album_id' INTEGER, 'date' INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Awards" ('id' INTEGER PRIMARY KEY, 'award_show_name' NUMBER, 'num_wins' INTEGER, 'num_noms' INTEGER)""")

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
    del wiki_dict['Totals']

    for winsnoms in wiki_dict:
        cur.execute("""SELECT MAX(id) FROM Awards""")
        count = cur.fetchone()[0]
        
        cur.execute(
            """INSERT OR IGNORE INTO Awards (id, award_show_name, num_wins, num_noms)
            VALUES (?, ?, ?, ?)""",
            (award_id, winsnoms, wiki_dict[winsnoms]['wins'], wiki_dict[winsnoms]['noms'])
        )
        award_id += 1
        conn.commit()
        if type(count) == int:
            if count % 25 == 0:
                if count == 125:
                    break
                else:
                    sys.exit()
                #exit program every 25 items
    return wiki_dict

def spotifyApi():
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

    return ids, albums

def update_spotify_data(ids, cur, conn, album_list):
    track_list = []
    song_id = 0
    #update album table
    count = 0
    for i in range(len(album_list)):
            cur.execute("""INSERT OR IGNORE INTO Albums (id, album_title) VALUES (?, ?)""", 
            (i, album_list[i].lower()))

    for id in ids:
        meta = sp.track(id)
        features = sp.audio_features(id)

        new_track_info = []
        #fetch track info
        name = meta['name'].lower()
        album = meta['album']['name'].lower()
        artist = meta['album']['artists'][0]['name'].lower()
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
            part="contentDetails, snippet, id, status",
            playlistId=playlist[album],
            maxResults = 50
        )
        response = request.execute()
        song_list = []
        items = response["items"]
        for i in items:
            sub_it = i["snippet"]
            title = sub_it["title"].lower()
            date = sub_it["publishedAt"][:10]
            digdate = int(date[:4]+date[5:7]+date[-2:])
            song_list.append((title, digdate))
        album_videos[album] = song_list
    for album in album_videos:
        for i in album_videos[album]:
            cur.execute("INSERT OR IGNORE INTO Music_Videos (title, date) VALUES (?,?)", (i[0],i[1]))
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

def avg_length_album(album, cur, conn):
    cur.execute("SELECT length FROM Songs JOIN albums ON albums.id = Songs.album_id WHERE album_title = (?)", (album,))
    song_lengths = cur.fetchall()
    song_len_list = []
    for i in song_lengths:
        song_len_list.append(i[0])
    avg = sum(song_len_list)/len(song_len_list)
    avg_in_min = avg /60000
    return avg_in_min

def most_popular_album(cur, conn):
    cur.execute("SELECT id FROM albums")
    album_ids = cur.fetchall()
    pop_dict = {}
    for i in album_ids:
        cur.execute("SELECT popularity FROM Songs WHERE album_id = (?)", (i[0],))
        pop_tup_list = cur.fetchall()
        pop_list = []
        for a in pop_tup_list:
            pop_list.append(a[0])
        if len(pop_list) != 0:
            avg = sum(pop_list)/len(pop_list)
            pop_dict[i[0]]= avg
        else:
            continue
    pop_id = sorted(pop_dict.items(), key=lambda x: x[1], reverse = True)[0][0]
    cur.execute("SELECT album_title FROM albums WHERE id = (?)", (pop_id,))
    top_album = cur.fetchone()[0]
    return top_album

def album_time(album, cur, conn):
    cur.execute("SELECT length FROM Songs JOIN albums ON albums.id = Songs.album_id WHERE album_title = (?)", (album,))
    length_list = cur.fetchall()
    song_len_list = []
    for i in length_list:
        song_len_list.append(i[0])
    total_length = sum(song_len_list)
    return total_length

def write_calculations(data):
    pass

def avg_rating_graph(cur, conn, data):
    pass

def avg_length_graph(cur, conn, data):
    pass

def total_length_graph(cur, conn, data):
    pass

def awards_chart(cur, conn):
    print("awards chart printing? or even running? acknowledge this function please")
    cur.execute("""SELECT award_show_name, num_wins, num_noms
                FROM Awards
                WHERE num_noms >= 32
                """)
    awards = cur.fetchall()
    name = []
    wins = []
    noms = []
    for i in range(len(awards)):
        name.append(awards[i][0])
        wins.append(awards[i][1])
        noms.append(awards[i][2])
    #confused
    x_axis = np.arange(len(name))
    legend = ["Wins", "Nominations"]

    plt.bar(x_axis +0.2, wins, width=0.4, label="Wins")
    plt.bar(x_axis -0.2, noms, width=0.4, label="Nominations")
    plt.ylabel("Number of Nominations or Wins")
    plt.xticks(x_axis, name, rotation=45, fontsize=8, ha='right', rotation_mode='anchor')
    plt.subplots_adjust(bottom=0.305)
    plt.legend(legend, loc= "best")
    plt.title("Taylor Swift's Most Nominated-for Award Shows")

    plt.show()
    

def pie_chart_album_lengths(cur, conn):
    cur.execute("SELECT length FROM Songs")
    all_lengths = cur.fetchall()
    all_list = []
    for i in all_lengths:
        all_list.append(i[0])
    total = sum(all_list)
    cur.execute("SELECT album_title FROM Albums")
    albums = cur.fetchall()
    fractions = {}
    for i in albums:
        time = album_time(i[0], cur, conn)
        percent = time/total * 100
        fractions[i[0]] = percent
    labels = fractions.keys()
    sizes = fractions.values()
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')
    ax1.legend(labels,
          title="Album",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))
    plt.show()
    return(plt)

def main():
    url = "https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Taylor_Swift"
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.text, 'html.parser')
    cur, conn = setUpDatabase('db_vol_7.db')
    #cur.execute('DROP TABLE IF EXISTS Awards')
    createTables(cur, conn)

    #wiki_dict = scrapeWiki(soup, cur, conn)
    #song_id_list, album_list = spotifyApi()
    #update_spotify_data(song_id_list, cur, conn, album_list)
    yt_data= youtubeAPI(cur, conn)
    awards_chart(cur, conn)
    #calculations and visualizations
    """
    for album in album_list:
        #x = str(avg_length_album(album, cur, conn))
        #print("average time of "+album+ " is "+ x + " minutes")
    pop= most_popular_album(cur, conn)
    print("The most popular album is "+ pop)
    wins = str(avg_winsnoms_ratio(cur, conn))
    print("On average, Taylor wins "+ wins + " awards for every nomination.")
    pie_chart_album_lengths(cur, conn)
    """

main()
