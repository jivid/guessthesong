#!/usr/bin/python
import sys
import argparse
import time

import tweepy
from get_lyrics import *

def follow_from(api, screen_name):
    count = 0
    for f in api.followers_ids(screen_name=screen_name):
        try:
            api.create_friendship(user_id=f, follow=True)
            count = count + 1
        except tweepy.error.TweepError as twperror:
            print("----  Caught exception  ----")
            print twperror
            print "Current count: %d" % count
            print("----------------------------")

        if ((count % 5) == 0) and (count != 0):
            print "Current count: %d. Sleeping for 60 seconds." % count
            time.sleep(180)

        if ((count % 100) == 0) and (count != 0):
            print "*** %d follower update ***" % count
            time.sleep(600)

        if (count == 250):
            return False

    print("Followed %d people from %s's twitter" % (count, screen_name))
    return True

def tweet(api, tweet_text):
    api.update_status(tweet_text)
    print("New tweet: %s" % (tweet_text))

def main():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    args = parser.parse_args()

    if args.follow_from is not None:
        target_screen_name = args.follow_from
        print "Going to follow all followers of %s" % (target_screen_name)
        verify = raw_input("Are you sure you want to continue? (y/n): ")
        if verify == 'y':
            done = follow_from(api, target_screen_name)
            if not done:
                print "Followed 250 people already. Can't do anymore"
                sys.exit(0)
        else:
            print("Exiting...")
            sys.exit(0)
    
    if args.tweet is not None:
        name, artist = get_song()
        
        song = Song()
        song.title = name
        song.artist = artist

        song.make_link()
        song.get_lyric()
        
        if song.lyric and song.check_if_exists():
            l = str(song.lyric)
            tweet_text = "%s #guessthesong #thelyricgame" % (l)
            print tweet_text

            verify = raw_input("Are you sure you want to continue? (y/n): ")
            if verify == 'y':
                song.write_to_db()
                print "Going to make tweet:\n%s\n" % (tweet_text)
                tweet(api, tweet_text)
            else:
                print("Exiting...")
                sys.exit(0)
        else:
            print "Lyric is empty. Doing nothing."
            sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Twitter guess-the-song bot")
    parser.add_argument('--tweet', '-t', help='Post a tweet')
    parser.add_argument('--list', '-l', help='List all tweets')
    parser.add_argument('--follow_from', '-F', help="Follow all followers of the specified user")

    CONSUMER_KEY = 'your_consumer_key'
    CONSUMER_SECRET = 'your_consumer_secret'
    ACCESS_KEY = 'your_access_key'
    ACCESS_SECRET = 'your_access_secret'

    main()
