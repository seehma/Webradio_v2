#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import logging

logger = logging.getLogger("webradio")

def getVariableFrom_MPD_Conf(var_string):
    ret = None
    conf_filepath = None

    if os.path.isfile("/etc/mpd.conf"):                                            # check systemconfig
        conf_filepath = "/etc/mpd.conf"

    if os.path.isfile(os.path.join(os.path.expanduser("~"), ".mpd", "mpd.conf")):
        conf_filepath = os.path.join(os.path.expanduser("~"), ".mpd", "mpd.conf")   # overwrite with first user conf

    if os.path.isfile(os.path.join(os.path.expanduser("~"), ".mpdconf")):
        conf_filepath = os.path.join(os.path.expanduser("~"), ".mpdconf")          # overwrite with second user conf

    logger.info("Load MPD Configfile: {0}".format(conf_filepath))
    #print("Load MPD Configfile: {0}".format(conf_filepath))

    with open(conf_filepath,"r") as conf_file:
        for line in conf_file:
            if line.startswith("#"):
                continue                # ignore comments in the conf-file
            elif line.startswith(var_string):
                ret = line.split(var_string)[1].strip().strip('"')
                logger.info("Searchkey {0} found: {1}".format(var_string, ret))
                return ret

    return ret  # if no entry was found starting with the keyword... ret = None


if __name__ == "__main__":
    print(getVariableFrom_MPD_Conf("music_directory"))