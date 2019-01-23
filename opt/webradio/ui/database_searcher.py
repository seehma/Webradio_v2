#!/usr/bin/python
# -*- coding: utf-8 -*-

#import players
import pprint
import copy
import sys
from PyQt4.QtCore import SIGNAL, QVariant, Qt, QString, QThread
from PyQt4.QtGui import QTreeWidget, QAbstractItemView, QApplication, QTreeWidgetItem, QIcon, QItemSelectionModel
import datetime
import time
import re
import commands
import logging
from httplib2 import ServerNotFoundError

logger = logging.getLogger("webradio")

from lib.googleapiclient.discovery import build
import pprint
pp = pprint.PrettyPrinter(indent=4)
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyDs9UiXmNXM_kWtWZWCJTtbYAJ90WQmChE"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
try:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY)
except ServerNotFoundError:
    logger.warning("Server can not reached, maybe no network is connected?")
    youtube = None

def iso_Date_to_seconds_int(timestring):
    '''
    This function converts an ISO8601 Sting to seconds (in int):
    P is the duration designator (for period) placed at the start of the duration representation.
    Y is the year designator that follows the value for the number of years.
    M is the month designator that follows the value for the number of months.
    W is the week designator that follows the value for the number of weeks.
    D is the day designator that follows the value for the number of days.
    T is the time designator that precedes the time components of the representation.
    H is the hour designator that follows the value for the number of hours.
    M is the minute designator that follows the value for the number of minutes.
    S is the second designator that follows the value for the number of seconds.
    Args:
        timestring:'PT3M38S'

    Returns: seconds in int, or -1 (Fail)
    '''
    if not timestring.startswith("P"):
        print("Timestring is not ISO8601 formated.")
        return -1

    match = re.search('^P.*T(?P<hours>[0-9]+)?H?(?P<minutes>[0-9]+)M?(?P<seconds>[0-9]+)S', timestring)
    if match:
        hours = int(match.groups(0)[0]) * 3600   # hours
        minutes = int(match.groups(0)[1]) * 60   # minutes
        seconds = int(match.groups(0)[2])
        return hours + minutes + seconds
    else:
        return -1

class Searchresult_Youtube(object):

    def __init__(self, parent=None):
        self.playlists= {}    # holds the playlists which are the searchresult, initially empty
        self.countPlaylists=0
        #self.playlists = self.__load_playlists(searchphrase, max_results)

    def load_playlists(self, query, max_results):

        # Call the search.list method to retrieve results matching the specified
        # query term.

        # max_results = the amount of downloaded playlist-infos

        search_response = youtube.search().list(
                          q=query,
                          type="playlist",   # video , channel ....
                          part="id,snippet",
                          maxResults=max_results
                          ).execute()
        items = []
        for search_result in search_response.get("items", []):

            if search_result["id"]["kind"] == "youtube#playlist":
                #pp.pprint(search_result)
                entry = {"id": search_result["id"]["playlistId"],
                         "size": None,
                         "title": search_result["snippet"]["title"],
                         "thumb": search_result["snippet"].get("thumbnails", {"default": {}, "high": {}})}
                # the "size" of a playlist is only included in a playlist itself...
                count = youtube.playlists().list(
                    part="snippet,contentDetails",
                    id=entry.get("id")
                     ).execute()["items"][0]["contentDetails"]["itemCount"]
                entry.update({"size": count})
                if count < 30:  # Load Playlists only with a maximum of 30 Tracks
                    if len(items) < 10:  # and so this for maximum 10 Playlists...
                        items.append(entry)
                    else:
                        break  # forget about the rest.

        results = {}
        ident = 0

        for item in items:
            link = item.get("id")                          #u'id': u'PLt3WBh3heAPuTrBkz0_-9c5kNXTds9wU3',
            size = item.get("size")                        #u'size': 15,
            title = item.get("title")                      #u'title': u'Top Tracks for Lana Del Rey',
            thumb = item.get("thumb")                      #u'title': u'Top Tracks for Lana Del Rey',
            playlist = Playlist(title, link, size, thumb, self)   #construct playlist-classes
            results.update({ ident : playlist})
            ident += 1

        self.playlists = results
        return results

    def playlist(self, ID):
        return self.playlists.get(int(ID))

    @property
    def count(self):
        return len(self.playlists)

    def __str__(self):
        representation = ""
        for ident, object in self.playlists.items():
            representation += "{0}, {1} ({2})\n".format(ident, object.title.encode("utf-8"), object.size)
        return representation

class Playlist(object):

    def __init__(self, title, link, size, thumb, parent=None):
        self.title = title
        self.size = int(size)
        self.link = link
        self.__thumb = thumb
        self.__tracks = None
        self.__restrictedCount = 0

    def listTracks(self):
        if self.__tracks is None:
            self.load_tracks()
        return self.__tracks

    def track(self, ID):
        return self.__tracks.get(int(ID))

    @property
    def count(self):
        if self.__tracks is None:
            self.load_tracks()
        return len(self.__tracks)

    @property
    def countRestricted(self):
        if self.__tracks is None:
            self.load_tracks()
        return self.__restrictedCount

    @property
    def thumb_HQ_link(self):
        return self.__thumb.get("high").get("url")

    @property
    def thumb_SQ_link(self):
        return self.__thumb.get("default").get("url")

    def load_tracks(self):
        """ Return a dict containing Track objects from a YouTube Playlist.

        The returned Pafy objects are initialised using the arguments to
        get_playlist() in the manner documented for pafy.new()

        """
        x = (r"-_0-9a-zA-Z",) * 2 + (r'(?:\&|\#.{1,1000})',)
        regx = re.compile(r'(?:^|[^%s]+)([%s]{18,})(?:%s|$)' % x)
        m = regx.search(self.link)

        if not m:
            err = "Unrecognized playlist url: %s"
            raise ValueError(err % self.link)

        videolist=[]

        playlistitems_list_request = youtube.playlistItems().list(
            playlistId=self.link,
            part="snippet",
            maxResults=50
        ).execute()

        for track in playlistitems_list_request["items"]:
            videolist.append(track["snippet"]["resourceId"]["videoId"])

        # playlist items specific metadata
        tracks = {}

        for i, v in enumerate(videolist):
            try:
                #https://developers.google.com/youtube/v3/docs/videos/list
                # Call the videos.list method to retrieve location details for each video.
                video_response = youtube.videos().list(
                    id=v,
                    part='snippet, contentDetails'
                ).execute()
                #pp.pprint(video_response)

                #check if video is "restricted" and override it.
                if video_response["items"][0].get('contentDetails').get("licensedContent"):
                #    self.__restrictedCount += 1
                    print("Licensed Content!", video_response["items"][0].get('snippet').get("title"))
                #    continue
                #else:
                title = video_response["items"][0].get('snippet').get("title")
                thumbnail = video_response["items"][0].get('snippet').get("thumbnails")
                encrypted_id = v
                duration = iso_Date_to_seconds_int(video_response["items"][0].get('contentDetails').get("duration"))

                trackobject = Track(title, thumbnail, encrypted_id, duration, self)
                tracks.update({i: trackobject})
            except IndexError:
                logger.warning("Ignored File id {0} because of a failure".format(v))

        self.__tracks = tracks

    def __str__(self):
        if self.__tracks is None:
            self.load_tracks()
        representation = ""
        for ident, object in self.__tracks.items():
            representation += "{0}, {1}\n".format(ident, object.title.encode("utf-8"))
        return representation

class Track(object):

    def __init__(self, title, thumbnail, encrypted_id, duration, parent=None):
        self.title = title
        self.thumbnails = thumbnail
        self.id = encrypted_id
        self.__duration = int(duration)
        self.expiration = None
        self.__streamlink = ""

    @property
    def streamLink(self):
        """
        :return: https://r4---sn-25g7sm7s.googlevideo.com/videoplayback?id=2515a8c7e8ba6809&itag=140
                 &source=youtube&requiressl=yes&pl=19&nh=EAI&mm=31&ms=au&mv=m&ratebypass=yes
                 &mime=audio/mp4&gir=yes&clen=4189911&lmt=1404272630358150
                 &dur=260.945&upn=2fbpK-GE08M
                 &signature=821C0B868E9A8AC68406546920651F04DD177CF1.765460B31D90954DFE42568639889C161FEF8B56
                 &fexp=901816,906388,938682,9407118,9407991,9408142,9408349,9408379,9408595,9408708,9408710,....
                 &mt=1431881298&sver=3&key=dg_yt0&ip=217.226.204.174&ipbits=0
                 &expire=1431902956
                 &sparams=ip,ipbits,expire,id,itag,source,requiressl,pl,nh,mm,ms,mv,ratebypass,mime,gir,clen,lmt,dur
        """
        if not self.isExpired() and self.__streamlink != "":
            # use already loaded link if it is still valid
            #print("Re-Use existing Streamlink")
            ret = self.__streamlink
        else:  #if self.expiration is None or self.__streamlink == "":
            # # initial case or link is expired. Load a new one, set new expiration
            #print("Link expired, reload")
            ret = commands.getoutput("youtube-dl --prefer-insecure -g -f140 -- {0}".format(self.id))
            #print ret
            if ret.startswith("http"):   #only if a link was returned
                try:
                    expiration = re.search("(?P<exp>&expire=[^\D]+)", ret).group("exp").split("=")[1]
                    self.expiration = datetime.datetime.fromtimestamp(int(expiration))   # a link expires in about 6 hours !!
                except:
                    logger.error("Expiration-Time can not be extracted from Link: {0}, "
                                 "setting to 2 hours".format(self.title.decode("utf-8")))
                    self.expiration = datetime.datetime.now() + datetime.timedelta(hours=2)  # choose a short exiration
                #Debug only, delete after dev
                #self.expiration = datetime.datetime.now() + datetime.timedelta(minutes=5)  # debug only!
            else:
                logger.error("Youtube-dl returned: {0}...".format(ret))  #log only the first 30 letters
                ret = ""

        self.__streamlink = ret

        return ret

    def isExpired(self):
        if self.expiration is not None and self.expiration > datetime.datetime.now():
            return False
        else:
            return True

    @property
    def duration(self):
        return time.strftime("%M:%S", time.gmtime(self.__duration))

    @property
    def thumb_HQ_link(self):
        return self.thumbnails.get("high").get("url")

    @property
    def thumb_SQ_link(self):
        return self.thumbnails.get("default").get("url")

    def __str__(self):
        return '{0}, {1}'.format(self.title, self.duration)


class Database_SearchEngine(object):

    def __init__(self, parent=None):
        pass

    def search_for_Phrase(self, service, searchphrase):
        """
        If searchstring as spaces where the filename hasnt, it will return no result
        If a searchstring containing spaces, and no searchresults are found, we will
        replace the space with "_"
        :param searchphrase: Searchstring as QString or String
        :return: dict like this:
        {   'albums': [{   'Lana Del Rey': 'Born to Die'}],
            'artists': ['Lana Del Rey'],
            'files': [],
            'titles': [   {   'album': 'Born to Die',
                              'artist': 'Lana Del Rey',
                              'artistsort': 'Del Rey, Lana',
                              'date': '2012',
                              'file': 'toplevel/LanaDelRay/Born to Die/1 - Born to Die.mp3',
                              'last-modified': '2012-03-24T13:56:04Z',
                              'time': '286',
                              'title': 'Born to Die',
                              'track': '1/12'},
                          {   'album': 'Born to Die',
                              'artist': 'Lana Del Rey',
                              'artistsort': 'Del Rey, Lana',
                              'date': '2012',
                              'file': 'toplevel/LanaDelRay/Born to Die/2 - Off to the Races.mp3',
                              'last-modified': '2012-03-24T13:56:36Z',
                              'time': '300',
                              'title': 'Off to the Races',
                              'track': '2/12'}, ....
        """

        self._service = service
        if self._service is None:
            return {}

        tag ={ 0 : "artist",
               1 : "album",
               2 : "title",
               3 : "filename" }

        #print("search for:", searchphrase)
        result_artist = self._service.search(tag[0], searchphrase)
        #print("result1")
        result_album = self._service.search(tag[1], searchphrase)
        #print("result2")
        result_title = self._service.search(tag[2], searchphrase)
        #print("result3")
        result_filename = self._service.search(tag[3], searchphrase)
        #print("result4")

        overall_searchresult = {}
        ############### Combine Searchresults to a overall dict
        if len(result_artist) > 0:
            overall_searchresult.update({"result_artist" : result_artist})
        else:
            overall_searchresult.update({"result_artist" : []})
        ########################################################             ARTIST
        if len(result_album) > 0:
            overall_searchresult.update({"result_album" : result_album})
        else:
            overall_searchresult.update({"result_album" : []})
        ########################################################             ALBUM
        if len(result_title) > 0:
            overall_searchresult.update({"result_title" : result_title})
        else:
            overall_searchresult.update({"result_title" : []})
        ########################################################             TITLE
        if len(result_filename) > 0:
            overall_searchresult.update({"result_filename" : result_filename})
        else:
            overall_searchresult.update({"result_filename" : []})
        ########################################################              FILENAME
        #print("OVERALL RESULT:",overall_searchresult)
        return self._construct_hirarchy_dict(self._clean_duplicates_return_cleaned_list(overall_searchresult))

    def _clean_duplicates_return_cleaned_list(self, originalDict):

        deltaList = []
        cleaned_result = []
        # collect all filenames which are found by previouse searchmethodes (artist, album, titel. ...)
        for key in originalDict.iterkeys():  #"result_artist","result_album","result_title","result_filename" == []
            for list_item in originalDict[key]: # list_item is a dict {'album': 'Born to Die', 'artist': 'Lana De....'}
                filename_already_detected = list_item["file"]
                if filename_already_detected not in deltaList:
                    cleaned_result.append(list_item)
                    deltaList.append(filename_already_detected)
        #print("Return cleaned results.")
        return cleaned_result # list containing all found dicts but without duplicates

    def _construct_hirarchy_dict(self, list_with_songsDicts):
        """

        :param list_with_songsDicts:
        [{'album': 'Born to Die', 'artist': 'Lana Del Rey', 'track': '10/12', 'title': 'Million Dollar Man',
        'last-modified': '2012-03-24T13:59:14Z', 'artistsort': 'Del Rey, Lana',
        'file': 'toplevel/LanaDelRay/Born to Die/10 - Million Dollar Man.mp3', 'time': '232', 'date': '2012'},
        {'album': 'Born to Die', 'artist': 'Lana Del Rey', 'track': '11/12', 'title': 'Summertime Sadness',
        'last-modified': '2012-03-24T13:59:34Z', 'artistsort': 'Del Rey, Lana',
        'file': 'toplevel/LanaDelRay/Born to Die/11 - Summertime Sadness.mp3', 'time': '265', 'date': '2012'},
        {'album': 'Born to Die', 'artist': 'Lana Del Rey', 'track': '12/12', 'title': 'This Is What Makes Us Girls',
        'last-modified': '2012-03-24T13:59:50Z', 'artistsort': 'Del Rey, Lana',
        'file': 'toplevel/LanaDelRay/Born to Die/12 - This Is What Makes Us Girls.mp3', 'time': '240', 'date': '2012'}]

        :return:
        { 'artists' : ["Lana Del Rey", "Unknown"],
          'albums'  : [{'Lana Del Rey': 'Born to Die'}],
          'titles'  : [{'album': 'Born to Die', 'artist': 'Lana Del Rey', 'track':'10/12', 'title':'Million Dollar Man',
                        'last-modified': '2012-03-24T13:59:14Z', 'artistsort': 'Del Rey, Lana',
                         'file': 'toplevel/LanaDelRay/Born to Die/10 - Million Dollar Man.mp3',
                         'time': '232', 'date': '2012'}, {.....}, {......}] #title is not empty or not existing
          'files'   : [{'last-modified': '2014-06-26T19:41:29Z',
                        'file': 'toplevel/black_hole_sun_Soundgarden.mp3',
                        'time': '346'}]                                     #can not be sorted to any artist or album
        """
        hirarchy_dict = {}
        # ARTISTS: create a list of all available artists:
        artistList = []
        for song in list_with_songsDicts:
            if song.has_key("artist"):
                if song["artist"] != "" and song["artist"] not in artistList:
                    artistList.append(song["artist"])

        # ALBUMS: create a list of all available albums:
        albumsList = []
        ignorelist = []
        for song in list_with_songsDicts:
            if song.has_key("album"):
                if song["album"] != "" and song["album"] not in ignorelist:
                    if song.has_key("artist"):
                        albumsList.append({song["artist"]: song["album"]})
                        ignorelist.append(song["album"])
                    else:
                        albumsList.append({"unknown": song["album"]})
                        ignorelist.append(song["album"])

        ################ Sort entrys of list_with_songDicts in titleList or in fileList
        # TITLES: create a list of song-dictionarys where the "title" entry is existing and not empty
        titlesList = []
        remaining_files = copy.deepcopy(list_with_songsDicts)
        for i in xrange(len(list_with_songsDicts)):
            if list_with_songsDicts[i].has_key("title"):
                #print("Has Title:", list_with_songsDicts[i]["file"])
                if list_with_songsDicts[i]["title"] != "":# and song["title"] not in titlesList:
                    #print("title is not empty")
                    if list_with_songsDicts[i]["title"] not in titlesList:
                        #print("title is not in List.")
                        titlesList.append(list_with_songsDicts[i])
                        #print("Append Song", list_with_songsDicts[i]["title"])
                        #print(i)
                        remaining_files.remove(list_with_songsDicts[i])

        # FILES: create a list of all remaining song-dicts
        filesList = []
        for song in remaining_files:
            filesList.append(song)

        hirarchy_dict.update({"artists" : artistList})
        hirarchy_dict.update({"albums" : albumsList})
        hirarchy_dict.update({"titles" : titlesList})
        hirarchy_dict.update({"files" : filesList})
        #print("return hirarchy dict")
        return hirarchy_dict


class LM_QTreeWidget(QTreeWidget):
    '''
    Special QTreewidget which is used to present searchresults from MPD Database-Search (Database-SearchEngine)
    '''

    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self.service = None
        self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.clicked.connect(self.checkSelection_clicked)
        self.expanded.connect(self.checkSelection_expanded)
        self.collapsed.connect(self.checkSelection_collapsed)
        self.setColumnCount(2)
        self.setHeaderHidden(True)
        self.setItemsExpandable(True)

    def populateTree(self, searchphrase, includeOnline=True):

        self.clear()
        self.childFromArtist = {}
        self.parentFromAlbum = {}
        self.childFromAlbum = {}
        self.parentFromTitle = {}
        self.counts = {}
        self.onlineresults ={}

        self.setHeaderLabels(["Artist/Album/Title"])
        #print("Check Service")
        if self.service is None:
            #print("Service is none")
            return False
        #print("construct searchengine")
        self.searchEngine = Database_SearchEngine()
        #print("Phrase:",searchphrase)
        self.emit(SIGNAL("start_loading"))

        #Search for Searchphrase with MPC on the local database...
        self.thread = None
        self.thread = WorkerThread(self.searchEngine.search_for_Phrase,
                                   self.service, searchphrase.toLocal8Bit())  # Request API using string
        self.thread.start()
        while not self.thread.isFinished():
            QApplication.processEvents()
        data = self.thread.result()

        if includeOnline:
            # Search for Searchphrase with Youtube on the youtube database...
            self.searchEngine2 = Searchresult_Youtube()
            #self.emit(SIGNAL("start_loading"))
            # self.onlineresults = self.searchEngine2.load_playlists(query=searchphrase, max_results="3")
            self.thread2 = None
            self.thread2 = WorkerThread(self.searchEngine2.load_playlists, searchphrase.toLocal8Bit(), "30")  # maxresult
            self.thread2.start()
            while not self.thread2.isFinished():
                QApplication.processEvents()
            self.onlineresults = self.thread2.result() or {}   # if none, we want an empty dict again
            pp.pprint(self.onlineresults)
            # self.onlineresults is a dict with Playlists

        #create toplevelitems  (Artist Folders)
        for artist in data['artists']:
            entry0 = QTreeWidgetItem(self, [artist.decode('utf-8')])
            entry0.setIcon(0, QIcon(":/folder.png"))
            self.parentFromAlbum[artist] = entry0

        #create Albums (child folders of Artists)
        for album in data['albums']:
            #print(album.values()[0])
            #print(type(album.values()[0]))
            parentOfAlbum = self.parentFromAlbum[album.keys()[0]]
            entry1 = QTreeWidgetItem(parentOfAlbum, [album.values()[0].decode('utf-8')])
            entry1.setIcon(0, QIcon(":/folder.png"))
            self.parentFromTitle[album.values()[0]] = entry1
            self.childFromArtist[album.keys()[0]] = entry1
            tmp_count = self.counts.get(parentOfAlbum)
            if tmp_count is None:
                self.counts[parentOfAlbum] = 1
            else:
                self.counts[parentOfAlbum] += 1

        #create titles (childs of Albums)
        for title in data['titles']:
            if title.has_key("album"):
                parentOfTitel = self.parentFromTitle[title["album"]]
            elif title.has_key("artist"):
                parentOfTitel = self.parentFromAlbum[title["artist"]]
            else:
                parentOfTitel = self.parentFromAlbum.get("Unknown Artist")
                if parentOfTitel is None:
                    entry0 = QTreeWidgetItem(self, ["Unknown Artist"])
                    entry0.setIcon(0, QIcon(":/folder.png"))
                    self.parentFromAlbum["Unknown Artist"] = entry0
                    parentOfTitel = entry0

            tmp_count = self.counts.get(parentOfTitel)
            if tmp_count is None:
                self.counts[parentOfTitel] = 1
            else:
                self.counts[parentOfTitel] += 1

            entry2 = QTreeWidgetItem(parentOfTitel, [title["title"].decode('utf-8')])
            entry2.setIcon(0, QIcon(":/mp3.png"))
            entry2.setData(0, Qt.UserRole, QVariant((title,)))
            if title.has_key("album"):
                self.childFromAlbum[title["album"]] = entry2
            elif title.has_key("artist"):
                self.childFromArtist[title["artist"]] = entry2
            else:
                self.parentFromAlbum[title["title"]] = entry2

        if len(data["files"]) > 0:
            parentOfTitel = self.parentFromAlbum.get("Unknown Artist")
            if parentOfTitel is None:
                entry0 = QTreeWidgetItem(self, ["Unknown Artist"])
                entry0.setIcon(0, QIcon(":/folder.png"))
                self.parentFromAlbum["Unknown Artist"] = entry0

            for filename in data['files']:
                #print(filename["file"])
                #print(type(filename["file"]))
                parentOfFilename = self.parentFromAlbum["Unknown Artist"]
                entry1 = QTreeWidgetItem(parentOfFilename, [filename["file"].split("/")[-1:][0].decode('utf-8')])
                entry1.setData(0, Qt.UserRole, QVariant((filename,)))
                entry1.setIcon(0, QIcon(":/mp3.png"))
                self.childFromAlbum["Unknown Artist"] = entry1
                tmp_count = self.counts.get(parentOfFilename)
                if tmp_count is None:
                    self.counts[parentOfFilename] = 1
                else:
                    self.counts[parentOfFilename] += 1

        if len(self.onlineresults) > 0:
            parentOfTitel = self.parentFromAlbum.get("Online-Playlists")
            if parentOfTitel is None:
                entry0 = QTreeWidgetItem(self, ["Online-Playlists"])
                entry0.setIcon(0, QIcon(":/folder.png"))
                self.parentFromAlbum["Online-Playlists"] = entry0

            for key, playlistopj in self.onlineresults.iteritems():
                parentOfPlaylist = self.parentFromAlbum["Online-Playlists"]
                #print(playlistopj.title)
                entry1 = QTreeWidgetItem(parentOfPlaylist, [unicode(playlistopj.title),
                                                            "[{0}]".format(playlistopj.size)])
                entry1.setData(0, Qt.UserRole, QVariant((playlistopj,)))
                entry1.setIcon(0, QIcon(":/folder.png"))   #playlists are folders...
                #self.childFromAlbum["Online-Playlists"] = entry1
                self.parentFromTitle[unicode(playlistopj.title)] = entry1
                self.childFromArtist[unicode(playlistopj.title)] = entry1
                tmp_count = self.counts.get(parentOfPlaylist)
                if tmp_count is None:
                    self.counts[parentOfPlaylist] = 1
                else:
                    self.counts[parentOfPlaylist] += 1

        # Add a count- Value beside of each searchresult.
        for key, val in self.counts.iteritems():
            print(key.text(0), val)
            key.setText(1, "[" + str(val) + "]")
        self.resizeColumnToContents(0)

        self.emit(SIGNAL("stop_loading"))

        print("Population finished.")
        return True

    def markAllChildrenFrom(self, Index):
        #print("idle because isReady is", self.model().isReady)
        childs = self.get_MP3_of_Folder_using_Index(Index)
        for child in childs:
            self.selectionModel().select(child, QItemSelectionModel.Select)

    def get_MP3_of_Folder_using_Index(self, QModelIndex):
        childlist = []
        #print(self.rowCount(QModelIndex))
        for i in xrange(self.model().rowCount(QModelIndex)):
            child = self.model().index(i,0, QModelIndex)
            if child.data(Qt.UserRole).toPyObject() is None:
                continue  # ignore children which are folders...
            elif isinstance(child.data(Qt.UserRole).toPyObject()[0], Playlist):
                continue  # ignore online-playlists which are folders in real...
            else:
                print(child.data(Qt.UserRole).toPyObject())
                childlist.append(child)
        return childlist

    def mark(self, Index):
        self.selectionModel().select(Index, QItemSelectionModel.Select)

    def unmark(self, Index):
        self.selectionModel().select(Index, QItemSelectionModel.Deselect)

    def toggleExpansion(self, Index):
        if self.isExpanded(Index):
            self.collapse(Index)
        else:
            self.expand(Index)
        return True

###########Logic zur Selektion und expand der Dateistruktur ###########################
    def checkSelection_expanded(self, *args):
        print("Expanded")
        initial_selection = self.selectedIndexes()
        childs = self.get_MP3_of_Folder_using_Index(args[0])
        #print("MP3 in Folder:", childs)
        trigger = True
        for child in childs:
            if child not in initial_selection:
                trigger = False
                break

        if trigger:
            # Mark Expanded node
            #print("mark")
            self.mark(args[0])
            # Mark all Childs from Node which are MP3
            #print("mark children")
            self.markAllChildrenFrom(args[0])
        else:
            self.unmark(args[0])
        self.resizeColumnToContents(0)

    def checkSelection_clicked(self, *args):
        print("Clicked")
        initial_selection = self.selectedIndexes()

        if args[0] in initial_selection:
            iamselected = True
        else:
            iamselected = False

        if args[0].parent() in initial_selection:
            myparentisselected = True
        else:
            myparentisselected = False

        #if os.path.isdir(self.model().filePath(args[0])):      #do not use os. calls because of network speed.
        if self.model().hasChildren(args[0]):
            print("Folder")
            iamafolder = True
            iamanonlineplaylist = False
            iamafile = False
        elif isinstance(args[0].data(Qt.UserRole).toPyObject()[0], Playlist):
            print("Playlist")
            iamafolder = True
            iamanonlineplaylist = True
            iamafile = False
        else:
            print("File")
            iamafolder = False
            iamanonlineplaylist = False
            iamafile = True

        #wenn ich ein ordner bin und ich markiert bin, dann werden alle meine childs markiert
        if iamafolder and iamselected:
            print("Iam a folder an i am selected")
            self.clearSelection()
            self.mark(args[0])
            if iamanonlineplaylist:
                if args[0].data(Qt.UserRole).toPyObject()[0].size > self.model().rowCount(args[0]):
                    #the playlist got more tracks than childs are under the playlist... load tracks and append childs.
                    self.loadPlaylistFromIndex(args[0])

            self.markAllChildrenFrom(args[0])
            #print("expand")
            self.expand(args[0])
        elif iamafolder and not iamselected:
            print("Iam a folder an i am not selected.")
            childs = self.get_MP3_of_Folder_using_Index(args[0])
            for child in childs:
                self.unmark(child)
        elif iamafile and iamselected:
            #check if all other mp3 from my parent are marked also
            otherchilds = self.get_MP3_of_Folder_using_Index(args[0].parent())
            trigger = True
            for child in otherchilds:
                if child not in initial_selection:
                    trigger = False
            if trigger:
                self.mark(args[0].parent())

        #wenn parentNode markiert ist und args nicht markiert ist, parent nicht mehr markieren
        if myparentisselected and not iamselected:
            parent = args[0].parent()
            #print("Unmark NOW:", parent, self.parentFromAlbum.get(parent))
            #while parent != self:
            self.unmark(parent)
            #    parent = parent.parent()

    def checkSelection_collapsed(self, *args):
        print("Collapsed")
        self.clearSelection()
        self.resizeColumnToContents(0)

    def get_current_selection(self):
        print("get current Selection")
        selection = self.selectedIndexes()
        filepathes = []
        for item in selection:
            if item.data(Qt.UserRole).toPyObject() is None:
                continue # ignore children which are folders...
            elif isinstance(item.data(Qt.UserRole).toPyObject()[0], Playlist):
                continue  # ignore online-playlists which are folders in real...
            else:
                if isinstance(item.data(Qt.UserRole).toPyObject()[0], Track):
                    #url = item.data(Qt.UserRole).toPyObject()[0].streamLink
                    #title = item.data(Qt.UserRole).toPyObject()[0].title
                    #filepathes.append(" ".join([url, title]))  # String: Url, Space, Title
                    filepathes.append(item.data(Qt.UserRole).toPyObject()[0])  #Trackobjekt
                else:
                    filepathes.append(item.data(Qt.UserRole).toPyObject()[0]['file'].decode('utf-8'))
        return filepathes

    def set_service(self, mpd_service):
        self.service = None
        self.service = mpd_service

    def loadPlaylistFromIndex(self, ModelIndex):
        playlist = ModelIndex.data(Qt.UserRole).toPyObject()[0]
        self.emit(SIGNAL("start_loading"))
        print("Request for Playlist")
        thread = WorkerThread(playlist.listTracks)
        thread.start()
        while not thread.isFinished():
            QApplication.processEvents()
        tracks = thread.result()
        print("Request Done.")
        #tracks = playlist.listTracks()

        for Id, trackObj in tracks.iteritems():
            title = trackObj.title
            print("Title:", title)
            print("Modelindex:", ModelIndex)

            parentOfTitel = self.itemFromIndex(ModelIndex)

            entry2 = QTreeWidgetItem(parentOfTitel, [unicode(title)])
            entry2.setIcon(0, QIcon(":/mp3.png"))
            entry2.setData(0, Qt.UserRole, QVariant((trackObj,)))
            self.parentFromAlbum[unicode(title)] = entry2
            print("Created: ", unicode(title))


        self.emit(SIGNAL("stop_loading"))


class WorkerThread(QThread):
    def __init__(self, function, *args, **kwargs):
        QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs

    #def __del__(self):
    #    self.wait()

    def run(self):
        #print("Start Process")
        self._result = None
        self._result = self.function(*self.args,**self.kwargs)
        #print("Process finished", self._result)
        return

    def result(self):
        return self._result


if __name__ == "__main__":

    searchphrase = raw_input("Enter Searchstring: ")
    app = QApplication([])
    window = LM_QTreeWidget()
    window.populateTree(searchphrase=QString(searchphrase))

    window.show()
    sys.exit(app.exec_())

# - die Suchergebisse sind aufgebaut wie :
#      +Nirvana
#          +Nevermind
#              Track1
#              Track2
#              Track3
#              .....
#          +Bleech
#              Track1
#              Track2
#              Track3
#              ....
#      +Sonstige
#          +Mixed MP3
#              Track1
#              Track2
#              Track3
#      Track_unknown1
#      Track_unknown2
#      ....
# - Die Tracks die hinzugefügt werden sollen können wie gewohnt ausgewählt werden und mittels eines speziellen
