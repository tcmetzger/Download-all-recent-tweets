"""Download most recent tweets for username
Store tweets in SQLite
"""

import argparse
import json
import time
import os
import urllib.request

import oauth2 as oauth

from db_stuff import create_connection, create_entry, does_entry_exist

# Read API tokens
CONSUMER_KEY = os.environ['CONSUMER_KEY']
CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
ACCESS_SECRET = os.environ['ACCESS_SECRET']
# Set to 200:
COUNT = 200  # max = 200
SLEEP_TIME = 1  # Sleep time between API calls


def parse_argument() -> str:
    """Parse command line option
    Return twitter screenname
    """
    parser = argparse.ArgumentParser(description='Retrieve all available tweets of user and inserts into SQLite database.')
    parser.add_argument('--screen_name', help='Screen name of user to be retrieved', required=True)
    args = parser.parse_args()
    user = args.screen_name.lower()
    return user


def oauth_header(url, consumer, token):
    """ Build oauth header
    Return header
    """
    params = {
        'oauth_version': '1.0',
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': str(int(time.time())),
        }
    req = oauth.Request(method='GET', url=url, parameters=params)
    req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, token)
    return req.to_header()['Authorization'].encode('utf-8')


def read_from_api(auth, url):
    """ Build api request and get data
    Return tweet_list (json)
    """
    req = urllib.request.Request(url)
    req.add_header("Authorization", auth)
    stream = urllib.request.urlopen(req).read()
    tweet_list = json.loads(stream.decode('utf-8'))
    return tweet_list


def parse_tweet(tweet):
    """ Parse elements of tweet into dict
    Return dict
    """
    tweet_dict = {
        'created_at': tweet['created_at'],
        'full_text': tweet['full_text'],
        'tweet_id': tweet['id_str'],
        'source': tweet['source'],
        'retweets': tweet['retweet_count'],
        'favorites': tweet['favorite_count'],
        'geo': str(tweet['geo']),
        'coordinates': str(tweet['coordinates']),
        'place': str(tweet['place']),
        'reply_to': tweet['in_reply_to_status_id'],
        'deeplink': f'https://twitter.com/{tweet["user"]["screen_name"]}/status/{tweet["id_str"]}'
        }
    return tweet_dict


def main():

    # Parse command line
    user = parse_argument()

    # Set URL and Headers (https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline)
    url = f'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={user}&count={str(COUNT)}'
    oauth_consumer = oauth.Consumer(key=CONSUMER_KEY, secret=CONSUMER_SECRET)
    oauth_token = oauth.Token(key=ACCESS_TOKEN, secret=ACCESS_SECRET)

    # Set up db
    database_name = user + '_retrieved.db'
    conn = create_connection(database_name)

    # Process data
    with conn:
        counter_new = 0  # count how many new entries were added to db
        counter_known = 0  # count how many entries are already known
        while True:
            # set up initial url
            first_url = url + '&tweet_mode=extended'
            # set up url and auth
            auth = oauth_header(first_url, oauth_consumer, oauth_token)
            # load data from API
            tweet_list = read_from_api(auth, first_url)
            # Iterate over downloaded data and store new items in db
            if len(tweet_list) > 1 and counter_known <= COUNT:
                last_id = 0
                for tweet in tweet_list:
                    tweet_dict = parse_tweet(tweet)
                    tweet_data = []
                    last_id = tweet_dict['tweet_id']
                    # translate tweet_dict into keyless tweet_data (list) for passing on to db
                    for key in tweet_dict.keys():
                        tweet_data.append(tweet_dict[key])
                    if not does_entry_exist(conn, tweet_dict['tweet_id']):
                        entry_id = create_entry(conn, tweet_data)
                        counter_new += 1
                        print(f'Tweet \"{tweet_dict["full_text"]}\" stored with id {entry_id}\n')
                    else:
                        print(f'Tweet \"{tweet_dict["full_text"]}\" already in db\n')
                        counter_known += 1
                if 'max_id' in url:
                    url = url.split('max_id')[0] + 'max_id=' + last_id + '&tweet_mode=extended'
                    print(url)
                else:
                    url = f'{url}&max_id={last_id}&tweet_mode=extended'
                    print(url)
                time.sleep(SLEEP_TIME)
            else:
                break
    print(f'\nFINISHED! {counter_new} new entries added to db!')


if __name__ == '__main__':
    main()
