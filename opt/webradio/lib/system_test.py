#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import logging
import os, ssl
from distutils import spawn

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None)):
    # dont need to verify ssl cert. just takes time...
    ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)

INTERNET = 'http://www.google.com'
RADIODE = 'http://radio.de'
LASTFM = 'http://www.lastfm.de'
WEATHERCOM = 'http://wxdata.weather.com/'

def test_onlineServices():
    logger.info("Probe online-services.")
    service_internet = False
    service_radiode = False
    service_lastfm = False
    service_weathercom = False

    result = {"internet": False,
              "radiode": False,
              "lastfm": False,
              "weathercom": False}

    try:                                                                    # check internet-connection
        urllib2.urlopen(INTERNET, timeout=1)
        service_internet = True
    except urllib2.URLError, e:                                                # if there is an error
        logger.error("Could not connect to {}: {}".format(INTERNET, e))
        return False, result

    if service_internet:
        try:                                                                    # check internet-connection
            urllib2.urlopen(RADIODE, timeout=1)
            service_radiode = True
        except urllib2.URLError, e:                                                # if there is an error
            logger.error("Radio.de can not be reached: {}".format(e))
            service_radiode = False

        try:                                                                    # check internet-connection
            urllib2.urlopen(LASTFM, timeout=5)  #seems like this server is sometimes slow.
            service_lastfm = True
        except urllib2.URLError, e:                                                # if there is an error
            logger.error("Last FM can not be reached: {}".format(e))
            service_lastfm = False
        except ssl.SSLError, e:
            # sometimes Last FM is terrible slow with SSL... ignore this (otherwise thie would prevent startup!)
            logger.warning('Ignore SSL Error during system-check')
            service_lastfm = True

        try:                                                                    # check internet-connection
            urllib2.urlopen(WEATHERCOM, timeout=1)
            service_weathercom = True
        except urllib2.URLError, e:                                                # if there is an error
            logger.error("Weather.com can not be reached: {}".format(e))
            service_weathercom = False

    #print("Internet:   ", service_internet)
    #print("Radio.de:   ", service_radiode)
    #print("lastfm.de:  ", service_lastfm)
    #print("weather.com:", service_weathercom)

    result.update({"internet": service_internet})
    result.update({"radiode": service_radiode})
    result.update({"lastfm": service_lastfm})
    result.update({"weathercom": service_weathercom})


    if service_radiode and service_lastfm and service_weathercom:
        return True, result
    else:
        return False, result

def test_serverconnection():
    pass

def test_usbconnection():
    pass

def test_programm_exists(name_executable):
    state = False
    path = spawn.find_executable(name_executable)
    if path is not None or path != "":
        logger.info("{0} is installed".format(name_executable))
        state = True
    else:
        logger.warning("{0} is not installed or can not be found".format(name_executable))
    return state

def isRunningWithSudo():
    # ATTENTION: Raspbian got a different behaviour on "expanduser" ... the file is not startet with root-privilegues
    # in fact the file is startet AS root ... this means the expanded ~ is /root.
    # to avoid this, we have to grab the sys-variable "SUDO_USER" ... but this can be None as well, if webradio
    # was startet witout "sudo" ...
    return True if os.getenv("SUDO_USER") else False

def signedInUserName():
    # ATTENTION: Raspbian got a different behaviour on "expanduser" ... the file is not startet with root-privilegues
    # in fact the file is startet AS root ... this means the expanded ~ is /root.
    # to avoid this, we have to grab the sys-variable "SUDO_USER" ... but this can be None as well, if webradio
    # was startet witout "sudo" ...
    return os.getenv("SUDO_USER") if os.getenv("SUDO_USER") else os.path.expanduser("~").split('/home/')[1]

if __name__ == "__main__":
    print("Check Online-Services...")
    status, results = test_onlineServices()

    if status:
        print("All Tests passed")
    else:
        print("At least one of the system-tests failed !")
        for key, value in results.iteritems():
            if not value:
                print("Please Debug:")
                print(key)




