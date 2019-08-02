# Webradio-py - A MPD-aided Music and Webradio Player for your Raspberry Pi:

The Python Script "webradio.py" for the Raspberry-Pi (Raspbian) or equivalent is a Python-Script used as a 
"Frontend" for the "MPD (Music-Player-Daemon)" with multiple advantages and additional features like:

- Search and manage webradio-stations with a GUI
- Listen to your local MP3-Music-Collection
- Search your MP3-Collection
- Automated Album-Cover download
- Use of embedded Album-Covers from your MP3's
- support for multiple File-Formats like .mp3, .ogg, .oga, and .flac
- Stream Music from Youtube
- Check the Weather-Forecast for you location
- Multiple and self-designable Themes
- Shutdown-Timer / Sleep-Timer
- GPIO integration (use Buttons for changing webradio-stations, shutdown, mount-/umount USB-Sticks aso.)
- Onscreen settings
- Screensaver-Mode

For a nearer description, please see the **[Wiki](https://github.com/Acer54/Webradio_v2/wiki/Home)**

On youtube, you can find a detailed video-presentation of an early Version1 (german only!):

[![Youtube-Video](http://img.youtube.com/vi/8zRfpBta6v8/0.jpg)](https://www.youtube.com/watch?v=8zRfpBta6v8)

Comparsion between Version2 (0.2.8) and Version1:

[![Youtube-Video](http://img.youtube.com/vi/oQ6oTWDCCFQ/0.jpg)](https://www.youtube.com/watch?v=oQ6oTWDCCFQ)

# Installation without receiving Updates
### 1. Download the current deb-package
from [releases](https://github.com/Acer54/Webradio_v2/releases)
### 2. Install it from a Terminal with
    sudo apt install ./webradio*
***

# Alternative Installation with Updates
### 1. Add a new source to your system:
    wget https://raw.githubusercontent.com/Acer54/repository/master/release/release.key && sudo apt-key add release.key && rm release.key
    wget "https://raw.githubusercontent.com/Acer54/repository/master/release/acer54_repository.list" && sudo mv acer54_repository.list /etc/apt/sources.list.d/
### 2. Update your sources:
    sudo apt update
### 3. Install webradio-py:
    sudo apt install webradio-py

## After Installation initialize your MPD-Database:
    mpc update

## Start webradio.py by:
* clicking on the radio-icon in your system menu \
or
* launch "sudo systemctl start webradio.service" from a terminal \
or 
* configure autostart

For a detailed description, please see ["Installation of webradio-py in my Wiki](https://github.com/Acer54/Webradio_v2/wiki/3_Installation-webradio-py)


Tested with 
 - "Raspbian Stretch", "Raspbian Buster";
