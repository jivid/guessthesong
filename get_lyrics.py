#!/usr/bin/python
import urllib2
import random
import datetime

from bs4 import BeautifulSoup
import MySQLdb

from twitter_cli import *

HOST = "db_host_name"
DB = "db_database"
USER = "db_user"
PASSWORD = "db_password"

class Song():
    def __init__(self):
        self.title = ""
        self.artist = ""
        self.link = ""
        self.lyric = ""

    def make_link(self):
        song_name = self.title.lower().replace("'",'').replace(' ', '-')
        song_artist = self.artist.lower().replace("'",'').replace(' ', '-')
        self.link = "http://www.lyrics.com/%s-lyrics-%s.html" % (song_name, song_artist)

    def get_lyric(self):
        page = urllib2.urlopen(self.link)
        soup = BeautifulSoup(page)

        try:
            lyric_set = soup.findAll('div', {'id': 'lyric_space'})
            lyrics = str(lyric_set[0]).replace('<br/>', '').split('\n')
        except IndexError:
            return False
        lines = len(lyrics)
        
        line_num = random.choice(range(5,lines-5))
        lyric = "%s, %s" % (lyrics[line_num], lyrics[line_num+1])

        if '<div' in lyric or '<ul' in lyric:
            self.get_lyric()
        elif (len(lyric) > 115):
            self.get_lyric()
        else:
            self.lyric = lyric

    def write_to_db(self):
        db = MySQLdb.connect(host=HOST, db=DB, user=USER, passwd=PASSWORD)
        cur = db.cursor()
        cur.execute("""INSERT INTO used_songs (song_name, song_artist) VALUES\
                    (`%s`, `%s`);""" % (self.title, self.artist))
        db.commit()
        db.close()
        print self.lyric
        print "Wrote '%s' by '%s' to the database" % (self.title, self.artist)

    def check_if_exists(self):
        db = MySQLdb.connect(host=HOST, db=DB, user=USER, passwd=PASSWORD)
        cur = db.cursor()
        q = """SELECT datetime FROM used_songs WHERE song_name=%s AND song_artist=%s"""
        exists = cur.execute(q, (str(self.title), str(self.artist)))
        if not exists:
            return True
        else:
            return False

    def tweet_lyric(self):
        '''
        Compose a tweet with the given lyric.
        '''

        resp = self.check_if_exists()
        tweet_text = ""
        if resp:
            tweet_text += "%s. #guessthesong #thelyricgame" % (self.lyric)

def get_song():
    lyrics_homepage = urllib2.urlopen("http://www.lyrics.com")
    lyric_soup = BeautifulSoup(lyrics_homepage)

    songs = lyric_soup.findAll('a', href=True)

    songs = songs[10:91]
    song_num = random.randrange(0,81,3)

    name = songs[song_num].contents[0]
    artist = songs[song_num+1].contents[0]

    return name, artist    

if __name__ == '__main__':
    sname, sartist = get_song()

    song = Song()
    song.title = sname
    song.artist = sartist

    song.make_link()
    song.get_lyric()
    song.write_to_db()
    
    print song.title
    print song.artist
    print song.lyric
