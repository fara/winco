import acoustid
import musicbrainzngs
import eyed3
import os
import json

"""
Fingerprint search with https://acoustid.org 
Album info search with https://musicbrainz.org/ 
"""

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MP3_DIR = os.path.join(BASE_DIR, 'mp3')
COVER_DIR = os.path.join(BASE_DIR, 'covers')
APIKEY = "******"
BRAINZ_USER = "******"
BRAINZ_PASS = "******"

if __name__== "__main__":

    musicbrainzngs.auth(BRAINZ_USER, BRAINZ_PASS)
    musicbrainzngs.set_useragent("Auto tag script", "0.1", "http://localhost")

    song = os.path.join(MP3_DIR, '3.mp3')
    for score, recording_id, title, artist in acoustid.match(APIKEY, song):
        # Get song data
        result_data = musicbrainzngs.get_recording_by_id(recording_id, includes=['artists','releases'])
        title = result_data['recording']['title']
        artist = result_data['recording']['artist-credit-phrase']
        print "%s - %s" % (title, artist)

        # Set ID3 tags
        audiofile = eyed3.load(song)
        audiofile.tag.artist = unicode(artist)
        audiofile.tag.title = unicode(title)

        # Get Cover Art
        if result_data['recording']['release-count']:
            imagedata = musicbrainzngs.get_image_front(result_data['recording']['release-list'][0]['id'])
            print audiofile.tag.images.set(eyed3.id3.frames.ImageFrame.FRONT_COVER, imagedata, 'image/jpeg')
            cover = open(os.path.join(COVER_DIR, result_data['recording']['release-list'][0]['title'] + '.jpg'), "w+")
            cover.write(imagedata)
            print "---"

        audiofile.tag.save()


