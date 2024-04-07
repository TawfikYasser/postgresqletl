import os
import glob
import psycopg2
import pandas as pd
from sqlQueries import *

def process_song_file(cur, filepath):
    """
    Load data from song file to the `song` and `artist` tables
    """

    df = pd.read_json(filepath, lines=True)

    # Insert song record
    song_data = list(df[['song_id', 'title' , 'artist_id', 'year', 'duration']].values[0])
    cur.execute(song_table_insert, song_data)

    # Insert artist record
    artist_data = list(df[['artist_id', 'artist_name', 'artist_location', 
                           'artist_latitude', 'artist_longitude']].values[0])
    cur.execute(artist_table_insert, artist_data)

def process_log_file(cur, filepath):
    """
    Load data from log file to the `time`, `user`, and `songplay` tables
    """

    df = pd.read_json(filepath, lines=True)

    df = df[df['page'] == 'NextSong']

    t = pd.to_datetime(df['ts'])

    # Insert time records
    time_data = [(tt.value, tt.hour, tt.day, tt.week, tt.month, tt.year, tt.weekday()) for tt in t]
    column_labels = ('timestamp', 'hour', 'day', 'week', 'month', 'year', 'weekday')
    time_df = pd.DataFrame(data=time_data, columns=column_labels)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # Load user table
    user_df = df[['userId', 'firstName', 'lastName', 'gender', 'level']]

    # Inser user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # Insert songplay records
    for index, row in df.iterrows():
        # Get song_id and artist_id from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # Insert songplay record
        songplay_data = (index, row['ts'], row['userId'], row['level'], songid, artistid,
                         row['sessionId'], row['location'], row['userAgent'])
        
        cur.execute(songplay_table_insert, songplay_data)

def process_data(cur, conn, filepath, func):

    """
    Iterate over all files and populate the data into the sparkifydb
    """

    # Get all files matching the extension from the directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, '*.json'))
        for f in files:
            all_files.append(os.path.abspath(f))

    # Get total number of files found
    num_files = len(all_files)
    print(f'Total number of files found in {filepath} is {num_files}')

    # Iterate over all files and process each file
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print(f'{i}/{num_files} files processed.')


def main():
    """
    Connect to the sparkifydb database

    Then run the ETL pipeline
    """

    conn = psycopg2.connect("host=172.23.0.3 dbname=sparkifydb user=postgres password=P@ssw0rd")

    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()