import json
import sys
import os
import matplotlib
import sqlite3
import csv
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np
from bs4 import BeautifulSoup
import requests
import unittest
import spotipy
import numpy as np
from spotipy.oauth2 import SpotifyClientCredentials #To access authorised Spotify data
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import itertools
import operator


cid = '80e4d2a8c2734c8e882a74e6f2c3e9bd'
secret = '9a43668b2bcc4b02a047683c2226defc'
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
<<<<<<< HEAD
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
=======
name = "{Taylor Swift}"
result = sp.search(name)
print(result['tracks']['items'][0]['artists'])


>>>>>>> 60c19a9b8cad86709d775858126604e6d7c9b207

#Phoebe, Shreya, Isabelle

def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

def createTables(cur, conn):
    #songs (title, album #, artist/collaborator #, song length, genre #, )
    #album ()
    #genre ()
    #awards?
    #music video (title, length, views, ?)
    cur.execute("DROP TABLE IF EXISTS Awards")
    cur.execute("DROP TABLE IF EXISTS Albums")
    cur.execute("DROP TABLE IF EXISTS Music_Videos")
    cur.execute("DROP TABLE IF EXISTS Songs")

    cur.execute("""CREATE TABLE IF NOT EXISTS 'Songs' 
        ('song_id' INTEGER PRIMARY KEY, 'song_title' TEXT, 'album_id' NUMBER, 
         'length' INTEGER, 'genre_id' NUMBER, 'popularity' INTEGER, 'danceability' REAL, 'energy' REAL)""")
        #am i missing anything? are we doing ratings
    cur.execute("""CREATE TABLE IF NOT EXISTS "Albums" ('id' INTEGER PRIMARY KEY, 'album_title' TEXT)""")
<<<<<<< HEAD
=======
    cur.execute("""CREATE TABLE IF NOT EXISTS "Genres" ('id' INTEGER PRIMARY KEY, 'genre_name' TEXT)""")
>>>>>>> 60c19a9b8cad86709d775858126604e6d7c9b207
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

def update_spotify_data(cur, conn, ids, albums):
    track_list = []
    id = 0
    song_id = 0
<<<<<<< HEAD
    #update album table
    count = 0
    for i in range(len(album_list)):
            cur.execute("""INSERT OR IGNORE INTO Albums (id, album_title) VALUES (?, ?)""", 
            (i, album_list[i].lower()))
=======
    album_no = 0

    for album in albums:
        cur.execute("""INSERT OR IGNORE INTO Albums (id, album_title) VALUES (?, ?)""", 
        (album_no, album))
        album_no += 1
>>>>>>> 60c19a9b8cad86709d775858126604e6d7c9b207

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

    return track_list

def get_song_ids(cur, conn):
    cur.execute(
        """
        SELECT Songs.song_id
        FROM Songs JOIN Music_Videos
        WHERE Music_Videos.song_name = Songs.song_title
        ORDER BY Music_Videos.song_name
        """
    )
    song_ids = cur.fetchall()
    append_ids = []
    for i in song_ids:
        append_ids.append(i[0])
    return append_ids

def youtubeAPI(cur, conn):
    api_service_name = "youtube"
    api_version = "v3"
    api_key = "AIzaSyDxoKyMEt6S3NdpT_yOIFTkSK3yWxQGbaE"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = api_key)
    
    playlist = {"red (taylor's version)": "OLAK5uy_lhEyrFap1OvMSwsL3AoZdrvqlRdJvyx0M",
                "fearless (taylor's version)": "OLAK5uy_lUwH9j_s3ZEeayUSm5o93gtQVz0If_kd8",
                "evermore":"OLAK5uy_m-vSVOiVeY_z2lPgThmS6Nn0TJExXZtOg",
                "folklore":"OLAK5uy_nWgO-2lNMsx90439Yx0xTWCGIktUc74e8",
                "lover":"OLAK5uy_nHHWc9S0Nw7oLyLYBptkJ4DpkQeoL1Igw",
                "reputation": "OLAK5uy_kyYsExXByLh2281MMfi0QvZJF5epEUxbk",
                "1989 (deluxe edition)":"OLAK5uy_lglIKPOFCG5X9_Rf4Hxsmmh9GEeHL94Jo",
                "speak now (deluxe edition)": "OLAK5uy_k_sq8Sp6KDtHZIxW6ovITiJhl6SIC-5gw",
                "message in a bottle (fat max g remix) (taylor’s version)":"OLAK5uy_n--XSLkZ2oX24BzALwE5oCHaBlPvx_L-I",
                "folklore: the long pond studio sessions (from the disney+ special) [deluxe edition]":"OLAK5uy_kBCcQO_p5kZzSJDsJ7wA5WSSQ_FUL4Xu0",
                "taylor swift": "OLAK5uy_l320Kcg2IKwpIRR07SD-ZejNX0cxRF32c",
                "speak now world tour live":"OLAK5uy_kWNYh2JP5uga3mbNeIxmgQOoW6cxPDzgw",
                }
    
    album_videos = {}
    vid_id = 0
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
            yt_id = i["id"]
            sub_it = i["snippet"]
            title = sub_it["title"].lower()
            date = sub_it["publishedAt"][:10]
            print(date)
            digdate = int(date[:4]+date[5:7]+date[-2:])
            song_list.append((title, digdate))
            #resp = youtube.videos().
        album_videos[album] = song_list
    for album in album_videos:
        cur.execute('SELECT id from Albums WHERE album_title = ?',([album]))
        album_id = int((cur.fetchone()[0]))
        for i in album_videos[album]:
            cur.execute("INSERT OR IGNORE INTO Music_Videos (title, date, id, album_id) VALUES (?,?,?,?)", (i[0],i[1],vid_id, album_id,))
            vid_id += 1
            conn.commit()
def updateAPI (cur, conn, data):
    pass
 
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
        if len(pop_list) <=2:
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

def danceable_album(cur, conn):
    cur.execute(
        """
        SELECT Songs.danceability, Albums.album_title 
        FROM Songs JOIN Albums
        WHERE Songs.album_id = Albums.id 
        """
    )
    res = cur.fetchall()
    album_avg_dict = {}
    num = 0.000
    count = 0
    name = ""   
    for key,group in itertools.groupby(res,operator.itemgetter(1)):
        sum = list(group)
        for i in sum:
            if count == 0:
                name = str(i[1])
            num += float(i[0])
            count += 1
        avg = num / count
        album_avg_dict[name] = avg
        num = 0.0000
        count = 0
    album_avg_dict = dict(sorted(album_avg_dict.items(), key=lambda item: item[1], reverse=True))
    fig = plt.figure(figsize = (10, 5))
    albums = list(album_avg_dict.keys())
    danceability = list(album_avg_dict.values())
    plt.barh(albums[:10], danceability[:10], color ='blue')
    plt.xlabel("Average Taylor Swift Album Danceability")
    plt.ylabel("Album Name")
    plt.yticks(fontsize = 8)
    plt.title("Danceability")
    plt.show()
    return res 

def videos_per_album(album, cur, conn):
    cur.execute("SELECT title FROM Music_Videos JOIN Albums ON albums.id = Music_Videos.album_id WHERE album_title = (?)", (album,))
    song_list = cur.fetchall()
    res = len(song_list)
    return res

def how_hard_was_taylors_yt_team_working_that_day(cur, conn):
    date_dict = {}
    cur.execute("SELECT date FROM Music_Videos")
    dates = cur.fetchall()
    for i in dates:
        cur.execute("SELECT title FROM Music_Videos WHERE date = ?", (i[0],))
        ls = cur.fetchall()
        date_dict[i[0]]=len(ls)
    return date_dict

def write_calculations(data):
    pass

def avg_rating_graph(cur, conn, data):
    pass

def avg_length_graph(cur, conn, data):
    pass

<<<<<<< HEAD
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
    

=======
>>>>>>> 60c19a9b8cad86709d775858126604e6d7c9b207
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
    clean_fractions = {}
    other = 0
    for i in fractions.keys():
        if fractions[i]<=1:
            other += fractions[i]
        else:
            clean_fractions[i]=fractions[i]
    clean_fractions['features and singles']= other
    labels = clean_fractions.keys()
    sizes = clean_fractions.values()
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, autopct='%1.1f%%',
            shadow=False, startangle=90)
    ax1.axis('equal')
    ax1.legend(labels,
          title="Album",
          loc="center left",
          bbox_to_anchor=(1, 0, 0.5, 1))
    plt.title("Fraction of Total Song Time on Each Album")
    plt.show()
    return(plt)

def energyvsdanceabilityplot(cur, conn):
    cur.execute("""SELECT danceability, energy FROM Songs""")
    res = cur.fetchall()
    danceability = []
    energy = []
    for i in res:
        danceability.append(i[0])
        energy.append(i[1])
    fig=plt.figure()    
    plt.scatter(danceability, energy, color='r')
    plt.xlabel('Danceability')
    plt.ylabel('Energy')
    plt.title('Danceability vs Energy Scatter Plot')
    plt.show()

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

=======
def video_bar_graphs(cur, conn):
    vid_dict = {}
    for album in album_list:
        x = videos_per_album(album.lower(), cur, conn)
        if x == 0:
            continue
        else:
            vid_dict[album[:21]] = x
    print(vid_dict)
    labels = vid_dict.keys()
    values  = vid_dict.values()
    fig1, ax1 = plt.subplots()
    ax1.bar(labels, values, color = "violet")
    plt.xticks(rotation = 45, rotation_mode = 'anchor', ha = 'right')
    plt.title("Number of Music Videos per Album")
    plt.xlabel("Album Name")
    plt.ylabel("Number of Videos")
    plt.show()

def main():
    url = "https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Taylor_Swift"
    page = requests.get(url, verify=False)
    soup = BeautifulSoup(page.text, 'html.parser')
<<<<<<< HEAD
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
=======
    cur, conn = setUpDatabase('db_vol_4.db')
    ids, albums = spotifyApi()
    createTables(cur, conn)
    scrapeWiki(soup, cur, conn)
    avg_winsnoms_ratio(cur, conn)
    print(update_spotify_data(cur, conn, ids, albums))
    youtubeAPI2 = youtubeAPI(cur, conn)
    print(youtubeAPI2)
    danceable_album(cur, conn)
    energyvsdanceabilityplot(cur, conn)


main()

#cur, conn = setUpDatabase('db_vol_8.db')
#cur.execute("DROP TABLE IF EXISTS Songs")
#cur.execute("DROP TABLE IF EXISTS Albums")
#cur.execute("DROP TABLE IF EXISTS Music_Videos")


>>>>>>> 60c19a9b8cad86709d775858126604e6d7c9b207
