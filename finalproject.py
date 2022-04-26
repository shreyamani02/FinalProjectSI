import sys
import os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from bs4 import BeautifulSoup
import requests
import spotipy
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
scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

#Phoebe, Shreya, Isabelle

"""This function creates the database specified by the input name, and returns 
the cursor and connection to edit the database"""
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

"""This function creates the Songs, Albums, Music_Videos, and Awards tables 
that will be filled in later. It inputs cur and conn, and it outputs nothing."""
def createTables(cur, conn):
    cur.execute("""CREATE TABLE IF NOT EXISTS 'Songs' 
        ('song_id' INTEGER PRIMARY KEY, 'song_title' TEXT, 'album_id' NUMBER, 
         'length' INTEGER, 'popularity' INTEGER, 'danceability' REAL, 'energy' REAL)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Albums" ('id' INTEGER PRIMARY KEY, 'album_title' TEXT)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Music_Videos" ('id' AUTO_INCREMENT INTEGER PRIMARY KEY, 'title' TEXT, 'album_id' INTEGER, 'date' INTEGER)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS "Awards" ('id' INTEGER PRIMARY KEY, 'award_show_name' NUMBER, 'num_wins' INTEGER, 'num_noms' INTEGER)""")
    conn.commit()

"""inputs a beautiful soup object and database cursor and connector. It scrapes
 the table of awards on Taylor Swift’s Wikipedia page, and adds the information 
 it gleans less than 25 items at a time, exiting the program each time. 
 There are 126 awards, so to completely add all data to the database the program 
 needs to be run 5 times. It returns nothing."""
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
    return wiki_dict

"""This function does not input anything. It uses spotipy to scrape a spotify 
playlist of all Taylor Swift songs. The Spotify API limits requests to 100 songs,
 so to get a complete list of data an offset method was used. The dictionary that 
 is returned from the API is parsed to create a list of song ids (used by spotify 
to identify the songs), and a list of each unique album in the playlist. It returns 
the list of song ids, and the list of albums."""
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

"""inputs the database cursor and connection, and the lists of song ids and albums.
 It then uses the album list to fill in the album table on the database. 
 The second part of the code uses the list of song ids to fetch the names, length, 
 popularity, danceability, and energy of the song, as well as the album id from the 
 album table. It returns nothing."""
def update_spotify_data(cur, conn, ids, album_list):
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

"""inputs the database cursor and connection, and uses a dictionary of Taylor 
Swift Music Video Playlists and their ids to identify each music video’s name, 
what album it belongs to, and what date it was last edited, and add this information 
to the Music Video table."""
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
            digdate = int(date[:4]+date[5:7]+date[-2:])
            song_list.append((title, digdate))
        album_videos[album] = song_list
    for album in album_videos:
        cur.execute('SELECT id from Albums WHERE album_title = ?',([album.lower()]))
        album_id = (cur.fetchone())
        if album_id == None:
            for i in album_videos[album]:
                cur.execute("INSERT OR IGNORE INTO Music_Videos (title, date, id) VALUES (?,?,?)", (i[0],i[1],vid_id,))
                vid_id += 1
                conn.commit()
        else:
            for i in album_videos[album]:
                cur.execute("INSERT OR IGNORE INTO Music_Videos (title, date, id, album_id) VALUES (?,?,?,?)", (i[0],i[1],vid_id, album_id[0],))
                vid_id += 1
                conn.commit()


"""inputs in the database cursor and connection, and accesses the database to 
compute and return the average ratio of wins and nominations for every award 
that she’s been nominated for."""
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
    return avg_ratio

""" inputs an album and database information. It  accesses the database, collects
 the album id and all the songs for that id, and finds the average length of a 
 song on that album. It returns this average length."""
def avg_length_album(album, cur, conn):
    cur.execute("SELECT length FROM Songs JOIN albums ON albums.id = Songs.album_id WHERE album_title = (?)", (album,))
    song_lengths = cur.fetchall()
    song_len_list = []
    for i in song_lengths:
        song_len_list.append(i[0])
    avg = sum(song_len_list)/len(song_len_list)
    avg_in_min = avg /60000
    return avg_in_min

"""inputs in the database cursor and connection and joins both the songs and 
albums table to calculate which album is the most popular. The function takes 
the sum of popularity for every song off the album and computes the average 
popularity based on the number of songs off the album."""
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

"""This function takes in the database cursor, connection, and the name of a 
specific album. Based on the album name, the function reads the length of every
 song on the album and computes the sum of all the lengths. It returns the total 
 length of the album. This function was used to make a pie chart."""
def album_time(album, cur, conn):
    cur.execute("SELECT length FROM Songs JOIN albums ON albums.id = Songs.album_id WHERE album_title = (?)", (album,))
    length_list = cur.fetchall()
    song_len_list = []
    for i in length_list:
        song_len_list.append(i[0])
    total_length = sum(song_len_list)
    return total_length

"""This function takes in the database information, and accesses the database 
to determine the average danceability score of each album. It then graphs this 
data, and returns the average danceability of all albums."""
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
    plt.barh(albums[:10], danceability[:10], color ='pink')
    plt.xlabel("Average Taylor Swift Album Danceability")
    plt.ylabel("Album Name")
    plt.yticks(fontsize = 8)
    plt.title("Danceability")
    plt.show()
    return res 

"""This function inputs the database information and an album name. The album 
name is used to access the album id and that is used to determine how many music
 videos correspond to that album. It returns an integer of music videos for that album."""
def videos_per_album(album, cur, conn):
    cur.execute("SELECT title FROM Music_Videos JOIN Albums ON albums.id = Music_Videos.album_id WHERE album_title = (?)", (album,))
    song_list = cur.fetchall()
    res = len(song_list)
    return res

"""This function inputs the database information and creates a dictionary of all
 days that the Taylor Swift Youtube Channel published a music video and the number
 of music videos published that day. """
def how_hard_was_taylors_yt_team_working_that_day(cur, conn):
    date_dict = {}
    cur.execute("SELECT date FROM Music_Videos")
    dates = cur.fetchall()
    for i in dates:
        cur.execute("SELECT title FROM Music_Videos WHERE date = ?", (i[0],))
        ls = cur.fetchall()
        date_dict[i[0]]=len(ls)
    return date_dict

"""This function prints out a bar graph that displays (top 10) the number of 
wins and nominations that Taylor has received at various award shows. The bars
 for nominations and wins are displayed in different colors."""
def awards_chart(cur, conn):
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
    x_axis = np.arange(len(name))
    legend = ["Wins", "Nominations"]

    plt.bar(x_axis +0.2, wins, width=0.4, label="Wins", color = "slateblue")
    plt.bar(x_axis -0.2, noms, width=0.4, label="Nominations", color = "lavender")
    plt.ylabel("Number of Nominations or Wins")
    plt.xticks(x_axis, name, rotation=45, fontsize=8, ha='right', rotation_mode='anchor')
    plt.subplots_adjust(bottom=0.305)
    plt.legend(legend, loc= "best")
    plt.title("Taylor Swift's Most Nominated-for Award Shows")

    plt.show()

"""This function creates a pie chart that displays the total length of each album
 as a fraction of the total time of Taylor’s discography. It inputs cur and conn, 
 and returns nothing. """
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

"""This function takes in a database cursor and connection and reads in the 
energy and danceability for every song in the database. It then plots the data 
on a scatterplot."""
def energyvsdanceabilityplot(cur, conn):
    cur.execute("""SELECT danceability, energy FROM Songs""")
    res = cur.fetchall()
    danceability = []
    energy = []
    for i in res:
        danceability.append(i[0])
        energy.append(i[1])
    fig=plt.figure()
    plt.scatter(danceability, energy, color='rebeccapurple')
    plt.xlabel('Danceability')
    plt.ylabel('Energy')
    plt.title('Danceability vs Energy Scatter Plot')
    plt.show()

"""This function takes in database information and the name of .txt file. 
It opens this file and runs the avg_length_album, most_pop_album, avg_winsnoms_ratio,
and videos_per_album function. It writes the results of these functions to the 
.txt file and closes the file. It returns nothing."""
def write_calculations(filename, cur, conn):
    path = os.path.dirname(os.path.abspath(__file__)) + os.sep
    outFile = open(path + filename, "w")
    line = "Taylor Swift Data Calculations: \n"
    outFile.write(line + "\n")
    line = "Average song length per album: \n"
    outFile.write(line + "\n")
    cur.execute("SELECT album_title FROM Albums \n")
    albums = cur.fetchall()
    for album in albums:
        x = str(avg_length_album(album[0], cur, conn))
        line = album[0]+ ":"+ x + " minutes"
        outFile.write(line + "\n")
    line = "Number of Music Videos per album: \n"
    outFile.write("\n"+ line + "\n")
    for album in albums:
        y = str(videos_per_album(album[0], cur, conn))
        line = album[0] + ": " + y
        outFile.write(line)
    pop= most_popular_album(cur, conn)
    line = "The most popular album is "+ pop +"\n"
    outFile.write(line + "\n")
    wins = str(avg_winsnoms_ratio(cur, conn))
    line = "On average, Taylor wins "+ wins + " awards for every nomination. \n"
    outFile.write(line + "\n")
    line = "Number of music videos published on Taylor Swift's Youtube each day: \n"
    outFile.write(line + "\n")
    dict = how_hard_was_taylors_yt_team_working_that_day(cur, conn)
    for i in dict.keys():
        date = str(i)
        num_vid = str(dict[i])
        line = date + ": " + num_vid
        outFile.write(line+"\n")
    line = "Taylor's Team was working really hard on March 24, 2022."
    outFile.write(line+"\n")
    line = "\n Phoebe's favorite song is Right Where You Left Me. \n Shreya's is Mr. Perfectly Fine. \n Isabelle's is Our Song."
    outFile.write(line)
    outFile.close()

"""his function inputs the database information and creates a matplotlib bar 
graph of the number of music videos for each album. It returns nothing. """
def video_bar_graphs(cur, conn):
    vid_dict = {}
    cur.execute("SELECT album_title FROM Albums")
    albums = cur.fetchall()
    for album in albums:
        album_name = album[0]
        x = videos_per_album(album_name.lower(), cur, conn)
        if x == 0:
            continue
        else:
            vid_dict[album_name[:21]] = x
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
    cur, conn = setUpDatabase('db_vol_13.db')
    createTables(cur, conn)
    wiki_dict = scrapeWiki(soup, cur, conn)
    song_ids, album_list = spotifyApi()
    update_spotify_data(cur, conn, song_ids, album_list)
    youtubeAPI(cur, conn)
    write_calculations("Calculations.txt", cur, conn)
    awards_chart(cur, conn)
    pie_chart_album_lengths(cur, conn)
    energyvsdanceabilityplot(cur, conn)
    video_bar_graphs(cur, conn)
    danceable_album(cur, conn)

main()






















