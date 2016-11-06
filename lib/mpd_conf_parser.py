#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import logging

logger = logging.getLogger("webradio")

def getVariableFrom_MPD_Conf(var_string):
    ret = None
    conf_filepath = None
    # ATTENTION: Raspbian got a different behaviour on "expanduser" ... the file is not startet with root-privilegues
    # in fact the file is startet AS root ... this means the expanded ~ is /root.
    # to avoid this, we have to grab the sys-variable "SUDO_USER" ... but this can be None as well, if webradio
    # was startet witout "sudo" ...
    home_dir = os.path.join("/home", os.getenv("SUDO_USER")) if os.getenv("SUDO_USER") else os.path.expanduser("~")

    if os.path.isfile("/etc/mpd.conf"):                                            # check systemconfig
        conf_filepath = "/etc/mpd.conf"

    if os.path.isfile(os.path.join(home_dir, ".mpd", "mpd.conf")):
        conf_filepath = os.path.join(home_dir, ".mpd", "mpd.conf")   # overwrite with first user conf

    if os.path.isfile(os.path.join(home_dir, ".mpdconf")):
        conf_filepath = os.path.join(home_dir, ".mpdconf")          # overwrite with second user conf

    logger.info("Load MPD Configfile: {0}".format(conf_filepath))
    #print("Load MPD Configfile: {0}".format(conf_filepath))

    with open(conf_filepath, "r") as conf_file:
        for line in conf_file:
            if line.startswith("#"):
                continue                # ignore comments in the conf-file
            elif line.startswith(var_string):
                ret = line.split(var_string)[1].strip().strip('"')
                if "~" in ret:    # exchange a tilde with the absolute path
                    logger.info("Expand User '~' with: {0}".format(home_dir))
                    ret = ret.replace("~", home_dir)
                logger.info("Searchkey {0} found: {1}".format(var_string, ret))
                return ret

    return ret  # if no entry was found starting with the keyword... ret = None


if __name__ == "__main__":
    print(getVariableFrom_MPD_Conf("music_directory"))