#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtGui import QWidget, QFont, QHBoxLayout, QSizePolicy, QSpacerItem, QVBoxLayout, QMainWindow, QLabel, \
    QApplication
from PyQt4.QtCore import Qt, QString, QTimer
import time
from datetime import datetime as date
import pyqapi as weather
import global_vars
import logging
import os

logger = logging.getLogger("webradio")

try:
    from lib.LM_Widgets_scaled_contents import Scaling_QLabel, Scaling_QLabel_pixmap
    from lib.weatherIcon import weatherIcon
except ImportError, e:
    logger.warning("Could not import required libraries: {}", e)
    from LM_Widgets_scaled_contents import Scaling_QLabel, Scaling_QLabel_pixmap
    from weatherIcon import weatherIcon



class Screensaver_Overlay(QWidget):
    '''
    Overlay for a window or widget below, just to display some content without blocking clicks to the window below.
    Just like a Screensaver.
    '''

    def __init__(self, cwd, weather_active=True, parent=None):
        super(Screensaver_Overlay, self).__init__(parent)
        self.cwd = cwd
        self.weather_active = weather_active
        self.setAttribute(Qt.WA_StyledBackground)    #want a styled Background
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setupUI()  # setup layout and widgets

        if parent is None:
            self.setFixedSize(600, 400)
        else:
            self.setFixedSize(parent.size())  # adapt size to parent (noramly the window)
        logger.info("Start Update-Cycle for Standby-Screensaver")
        self.startUpdate()  # start counters to periodically update conditions

    def setupUI(self):
        '''
        Setup of GUI Elements
        '''

        #setup Layout
        self.setStyleSheet("Screensaver_Overlay { background-color: black } "
                           "QLabel { color : white; }")
        font_max_time = QFont()
        font_max_time.setPointSize(94)

        font_max_date = QFont()
        font_max_date.setPointSize(34)

        self.horizontalLayout_3 = QHBoxLayout(self)
        self.horizontalLayout_2 = QHBoxLayout()
        self.verticalLayout = QVBoxLayout()
        spacerItem = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.lbl_time = Scaling_QLabel(self)
        self.lbl_time.setFont(font_max_time)
        self.lbl_time.setTextFormat(Qt.AutoText)
        self.lbl_time.setScaledContents(False)
        self.lbl_time.setWordWrap(True)
        self.lbl_time.maxFont = font_max_time
        self.lbl_time.setAlignment(Qt.AlignCenter)

        self.verticalLayout.addWidget(self.lbl_time)

        self.horizontalLayout = QHBoxLayout()

        self.lbl_day = Scaling_QLabel(self)
        self.lbl_day.setFont(font_max_date)
        self.lbl_day.setTextFormat(Qt.AutoText)
        self.lbl_day.setScaledContents(False)
        self.lbl_day.setWordWrap(True)
        self.lbl_day.maxFont = font_max_date
        self.lbl_day.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.horizontalLayout.addWidget(self.lbl_day)

        self.lbl_date = Scaling_QLabel(self)
        self.lbl_date.setFont(font_max_date)
        self.lbl_date.setTextFormat(Qt.AutoText)
        self.lbl_date.setScaledContents(False)
        self.lbl_date.setWordWrap(True)
        self.lbl_date.maxFont = font_max_date
        self.lbl_date.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.horizontalLayout.addWidget(self.lbl_date)

        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem1 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        spacerItem2 = QSpacerItem(14, 51, QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem2)
        self.verticalLayout_2 = QVBoxLayout()
        spacerItem3 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem3)

        #self.lbl_weather_icon = Scaling_QLabel_pixmap(self)
        self.lbl_weather_icon = weatherIcon(self)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_weather_icon.sizePolicy().hasHeightForWidth())
        self.lbl_weather_icon.setSizePolicy(sizePolicy)
        self.lbl_weather_icon.setScaledContents(False)
        self.lbl_weather_icon.setAlignment(Qt.AlignCenter)

        self.verticalLayout_2.addWidget(self.lbl_weather_icon)

        self.lbl_temperature = Scaling_QLabel(self)
        self.lbl_temperature.setFont(font_max_date)
        self.lbl_temperature.setTextFormat(Qt.AutoText)
        self.lbl_temperature.setScaledContents(False)
        self.lbl_temperature.setWordWrap(True)
        self.lbl_temperature.maxFont = font_max_date
        self.lbl_temperature.setAlignment(Qt.AlignCenter)

        self.lbl_temperature.setAlignment(Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.lbl_temperature)
        spacerItem4 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.horizontalLayout_2.setStretch(0, 2)
        self.horizontalLayout_2.setStretch(2, 1)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)


        self.lbl_time.setText("")
        self.lbl_day.setText("")
        self.lbl_date.setText("")
        self.lbl_temperature.setText(QString.fromUtf8(""))
        #self.lbl_weather_icon.setPixmap(QPixmap("../res/weather/icon/na.png"))
        self.setLayout(self.horizontalLayout_3)

    def startUpdate(self):
        '''
        This is called during initialisation and updates the content of the lables for time and weather
        '''
        timerclock = QTimer(self)
        timerclock.timeout.connect(self.updateTime)
        timerclock.start(1000)  # every second update the time
        if self.weather_active:
            timerclock2 = QTimer(self)
            timerclock2.timeout.connect(self.updateWeather)
            self.updateWeather() # initially make a call to the API to get the current condition
            timerclock2.start(300000)  #every 5 Minutes update the weather icon  (this will cause an API call...)

    def updateTime(self):
        '''
        This function is called by a QTimer with 1 sec. interval,
        Updates the current Time, Day and Date
        '''
        self.lbl_time.setText(self.tr(time.strftime("%H:%M")))
        self.lbl_day.setText(self.tr(date.today().strftime("%A")) + ", ")
        self.lbl_date.setText(self.tr(date.today().strftime("%d.%b.%Y").decode("utf-8")))  # avoid uft-8 problem with "März"

    def updateWeather(self):
        '''
        This function is called by a QTimer with 5 min. interval,
        Updates the weather-icon and the temperature
        '''
        location_ID = global_vars.configuration.get("GENERAL").get("weather_locationid")
        if location_ID is None:
            return   #return if no location ID can be loaded...
        temp_condition = weather.get_weather_from_weather_com(location_ID)
        self.lbl_weather_icon.setPicturePath(os.path.join(self.cwd, "res/weather/icon",
                                                          temp_condition['current_conditions']['icon'], "static"))

        self.lbl_temperature.setText(temp_condition['current_conditions']['temperature']+QString.fromUtf8("°C"))



class Testwindow(QMainWindow):
    '''
    A stupid empty window just displaying when it is receiving a click
    '''
    def __init__(self, parent=None):
        super(Testwindow, self).__init__(parent)
        self.resize(600,400)
        self.lbl = QLabel()
        self.setCentralWidget(self.lbl)

        self.overlay = Screensaver_Overlay(self)
        self.overlay.hide()

    def mousePressEvent(self, event):
        self.lbl.setText("Press at {0}".format(event.pos()))
        self.overlay.show()
        return QMainWindow.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        self.lbl.setText("Release at {0}".format(event.pos()))
        self.overlay.hide()
        return QMainWindow.mouseReleaseEvent(self, event)


if __name__ == '__main__':

    app = QApplication([])
    window = Testwindow()
    #window = Screensaver_Overlay()
    window.show()
    app.exec_()









