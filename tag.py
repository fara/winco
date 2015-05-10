import acoustid
import musicbrainzngs
import eyed3
import json
import time

from os import listdir, path, rename
from os.path import isfile, join, dirname

"""
Fingerprint search with https://acoustid.org 
Album info search with https://musicbrainz.org/ 
"""

BASE_DIR = dirname(dirname(__file__))
INBOX_DIR = path.join(BASE_DIR, 'in')
STORE_DIR = path.join(BASE_DIR, 'store')
COVER_DIR = path.join(BASE_DIR, 'covers')
APIKEY = "******"
BRAINZ_USER = "******"
BRAINZ_PASS = "******"


def tag_file(song_file):

    musicbrainzngs.auth(BRAINZ_USER, BRAINZ_PASS)
    musicbrainzngs.set_useragent("Auto tag script", "0.1", "http://localhost")

    #song = path.join(MP3_DIR, '3.mp3')
    print song_file
    for score, recording_id, title, artist in acoustid.match(APIKEY, song_file):
        # Get song data
        result_data = musicbrainzngs.get_recording_by_id(recording_id, includes=['artists','releases'])
        title = result_data['recording']['title']
        artist = result_data['recording']['artist-credit-phrase']
        print "%s - %s" % (title, artist)

        # Set ID3 tags
        audiofile = eyed3.load(song_file)
        audiofile.tag.artist = unicode(artist)
        audiofile.tag.title = unicode(title)

        # Get Cover Art
        if result_data['recording']['release-count']:
            try:
                imagedata = musicbrainzngs.get_image_front(result_data['recording']['release-list'][0]['id'])
                print audiofile.tag.images.set(eyed3.id3.frames.ImageFrame.FRONT_COVER, imagedata, 'image/jpeg')
                cover = open(path.join(COVER_DIR, result_data['recording']['release-list'][0]['title'] + '.jpg'), "w+")
                cover.write(imagedata)
                print "---"
            except musicbrainzngs.musicbrainz.ResponseError:
                pass

        audiofile.tag.save()



if __name__== "__main__":


    onlyfiles = [ f for f in listdir(INBOX_DIR) if isfile(join(INBOX_DIR,f)) ]
    for f in onlyfiles:
        if path.splitext(f)[1] == ".mp3":
            print f
            tag_file(path.join(INBOX_DIR, f))
            rename(path.join(INBOX_DIR,f), path.join(STORE_DIR, "%s.mp3" % time.time()))

    

