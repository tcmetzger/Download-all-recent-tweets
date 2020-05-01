"""Provide functions to setup and query SQLite database
"""

import sqlite3


def create_connection(db_file):
    """ Create a database connection to the SQLite database
    specified by db_file, create db and tables if required
    :param db_file: Database file
    :return: Connection object or None (in case of error)
    """
    sql_create_tweets_table = """CREATE TABLE IF NOT EXISTS tweets (
                                    id integer PRIMARY KEY,
                                    created_at text,
                                    full_text text,
                                    tweet_id integer,
                                    source text,
                                    retweets integer,
                                    favorites integer,
                                    geo text,
                                    coordinates text,
                                    place text,
                                    reply_to integer,
                                    deeplink text
                                );"""

    # connect to db file
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        raise NotImplementedError(f'Connection failed with msg {e}')

    # create tables if they don't exist
    try:
        c = conn.cursor()
        c.execute(sql_create_tweets_table)
    except sqlite3.Error as e:
        raise NotImplementedError(f'Execution failed with msg {e}')
    # return conn if db file and table are correct
    return conn


def create_entry(conn, tweet):
    """ Store new tweet in db
    :param conn: DB connection
    :param story: Tweet data
    :return: Row id of new tweet
    """

    sql = ''' INSERT INTO tweets(created_at,full_text,tweet_id,source,retweets,favorites,geo,coordinates,place,reply_to,deeplink)
              VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
    try:
        cur = conn.cursor()
        cur.execute(sql, tweet)
    except sqlite3.Error as e:
        raise NotImplementedError(f'Insertion failed with msg {e}')

    return cur.lastrowid


def does_entry_exist(conn, tweet_id):
    """ Check weather entry with exact tweet_id already exists
    :param conn: DB connection
    :param tweet_id: tweet_id to check
    :return: True if story already in db, else False
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tweets WHERE tweet_id=?", (tweet_id,))

    rows = cur.fetchall()

    if len(rows) > 0:
        return True

    else:
        return False
