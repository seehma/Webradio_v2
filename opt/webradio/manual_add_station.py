#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, pickle, sys, urllib, urllib2

user_dir = os.path.join("/home/", os.getenv("SUDO_USER") if os.getenv("SUDO_USER") else os.path.expanduser("~").split('/home/')[1], ".webradio")
LogoFolder = os.path.join(user_dir, "Logos")

class RadioStation(object):

    def __init__(self, name, station_id, url, fav=None, parent=None):
        self.name = name
        self.id = station_id
        self.fav = fav
        self.url = url

    def isFavorite(self):
        return self.fav

    def setAsFavorite(self):
        self.fav = True

    def unsetFavorite(self):
        self.fav = False

class UserInterface(object):

    def __init__(self):
        self._loadFavorites()   #read the current content from the stored favorites
        self.ui_loop()

    def _loadFavorites(self):
        basename = "favorites"
        extention = "fav"

        Openfile = os.path.join(user_dir, "{0}.{1}".format(basename, extention))
        if os.path.isfile(Openfile):
            self.favorites = pickle.load(open(Openfile, "rb" ) )
            print("Found Favorites: {0}".format(Openfile))
        else:
            print("No stored Favorites found.")
            self.favorites = {}

    def saveFavorites(self):
        """
        Save current favories in a dumped file on the HDD, the format is "{}".
        Also favorites will be saved in m3u format, in order to be able to call favories with a remote

        :return: [#STATION_ID \n http://url.for.mp3stream, ]
        """
        container = self.favorites
        favlist = []
        for key in self.favorites.iterkeys():
            favlist.append("#%d" %key)
            favlist.append(self.favorites[key].url)
        basename = "favorites"
        extention = "fav"

        filename = os.path.join(user_dir, "{0}.{1}".format(basename, extention))

        try:
            pickle.dump(container, open(filename, "wb"))

        except Exception, e:
            print("Could not save favorites to {}: {}".format(filename, e))
            return (False, [])
        print("Stored Favorites to: {0}".format(filename))
        return (True, self.writePlaylist("favorites", favlist))

    def writePlaylist(self, name, listOfContent):
        """
        Write a m3u playlist to a given name[.m3u] and fill it with the given list of Content, every item is written in
        a separate line into the file
        :param name: "favorites"
        :param listOfContent: [ "#2312", "http://url.to.mp3steam", "#2313", "http://next.url"]
        :return: True or False
        """
        basename = name
        extention = "m3u"
        #logger.debug("Writing new Playlistcontent: {0}".format(listOfContent))
        filename = os.path.join(user_dir, "{0}.{1}".format(basename, extention))
        try:
            with open(filename, "w") as playlistfile:
                for item in listOfContent:
                    playlistfile.write("%s\n" % item)
        except Exception, e:
            print("Could not write playlist to {}: {}".format(filename, e))
            return False
        return True

    def downloadstationLogoByURL(self, LogoUrl, stationID):
        """
        This function downloads and sets the Logo for a radio-station by using its Logo-URL and stationID (this is used
        for the name, under which the logo-file is stored.

        :param LogoUrl: "http://www.the-url-for-the-logo/logo.png
        :param stationID: 6415
        :return: True or False
        """
        if LogoUrl.endswith(".jpg"):
            extention = "jpg"
        elif LogoUrl.endswith(".jpeg"):
            extention = "jpeg"
        elif LogoUrl.endswith(".png"):
            extention = "png"
        else:
            #lets try it with an png
            extention = "png"

        fileToImport = os.path.join(LogoFolder, "{0}.{1}".format(stationID, extention))

        try:
            urllib.urlretrieve(str(LogoUrl), filename=fileToImport)
        except Exception, e:
            print("Error downloading Logo: {}".format(e))
            return False
        else:
            return True

    def ui_loop(self):

        user_input = None
        while user_input != "5":
            print("=================")
            print("Main Menue:")
            print("[1] List current favorites")
            print("[2] Add new station")
            print("[3] Delete station with ID")
            print("[4] Save & Exit")
            print("[5] Exit & discard changes")
            user_input = raw_input("Enter a Number (1-5):")

            if user_input == "1":
                if len(self.favorites) == 0:
                    print("[EMPTY]")
                for key in self.favorites.iterkeys():                    # for every entry in favorites dict
                    print("ID:{0} - Name:{1}".format(key, self.favorites[key].name))
            elif user_input == "2":
                user_input_newId = raw_input("Enter a unique ID-No. e.g. 9999:")
                user_input_newName = raw_input("Enter the Station-Name:")
                user_input_newURI = raw_input("Enter the streaming-URL (pls or m3u or direct link):")
                user_input_newLogo = raw_input("(optional) Enter a Logo-URL:")

                if user_input_newURI.endswith("m3u"):
                    #EXTM3U
                    #EXTINF:0,ROCK ANTENNE
                    #http://mp3channels.webradio.rockantenne.de/rockantenne
                    links =[]
                    m3u = urllib2.urlopen(user_input_newURI).read()
                    for line in m3u.splitlines():
                        if line.startswith("http"):
                            links.append(line)
                    if len(links) > 1:
                        print("There are more than one streaming-links included:")
                        i = 0
                        for entry in links:
                            print("{0} : {1}".format(i, entry))
                            i+=1
                        choice= int(raw_input("Choose from the listed Streaming-Links:"))
                        user_input_newURI = links[choice]
                    elif len(links) == 1:
                        user_input_newURI = links[0]
                    else:
                        print("Sorry, there was no streaming-Link identidied!")
                        user_input_newURI = ""

                    pass
                elif user_input_newURI.endswith("pls"):
                    #[playlist]
                    #numberofentries=1
                    #File1=http://mp3channels.webradio.rockantenne.de/rockantenne.aac
                    #Length1=-1
                    links =[]
                    pls = urllib2.urlopen(user_input_newURI).read()
                    for line in pls.splitlines():
                        if line.startswith("File"):
                            link=line.split("=")[1]
                            links.append(link)
                    if len(links) > 1:
                        print("There are more than one streaming-links included:")
                        i = 0
                        for entry in links:
                            print("{0} : {1}".format(i, entry))
                            i+=1
                        choice= int(raw_input("Choose from the listed Streaming-Links:"))
                        user_input_newURI = links[choice]
                    elif len(links) == 1:
                        user_input_newURI = links[0]
                    else:
                        print("Sorry, there was no streaming-Link identidied!")
                        user_input_newURI = ""


                if user_input_newId != "" and user_input_newName != "" and user_input_newURI != "":
                    new_station = RadioStation(user_input_newName, int(user_input_newId),user_input_newURI,True)
                    self.favorites.update({new_station.id: new_station})
                    if user_input_newLogo != "":
                        print("Start downloading of Station-Logo")
                        self.downloadstationLogoByURL(user_input_newLogo, new_station.id)

            elif user_input == "3":
                user_input_rmkey = raw_input("Enter the ID of the station which should be removed:")
                if self.favorites.pop(int(user_input_rmkey), None) is None:
                    print("Sorry, ID {0} was not found in your list.".format(user_input_rmkey))
            elif user_input == "4":
                self.saveFavorites()
                sys.exit(0)
            elif user_input == "5":
                sys.exit(0)
            else:
                print("Not allowed, please enter a number between 1 and 5!")

if __name__ == "__main__":
    myUI = UserInterface()
