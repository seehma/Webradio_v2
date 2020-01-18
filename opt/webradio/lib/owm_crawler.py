#!/bin/env python
# -*- coding: utf-8 -*
try:
    # Python 3 imports
    from urllib.request import urlopen
    from urllib.parse import quote
    from urllib.parse import urlencode
    from urllib.error import URLError
except ImportError:
    # Python 2 imports
    from urllib2 import urlopen
    from urllib import quote
    from urllib import urlencode
    from urllib2 import URLError
import json
import datetime
import logging
logger = logging.getLogger(__name__)

API_key = "&appid=a1bdebe52cea5f154dd5d37b744ace7e"     # 60 calls per minute max! (in total from all clients)
URL= "https://api.openweathermap.org/data/2.5/forecast?id={LOCATION_ID}{API_key}&units=metric"
SEARCH_URL = "https://api.openweathermap.org/data/2.5/find?callback=?&q={SEARCH_STRING}&type=like&sort=population&cnt=30&{API_key}"

ICON_TRANSLATION = {"01d": "32",
                    "01n": "31",
                    "02d": "28",
                    "02n": "27",
                    "03d": "30",
                    "03n": "29",
                    "04d": "30",
                    "04n": "29",
                    "09d": "11",
                    "09n": "11",
                    "10d": "39",
                    "10n": "45",
                    "11d": "47",
                    "11n": "47",
                    "13d": "41",
                    "13n": "46",
                    "50d": "20",
                    "50n": "20"}

def degToCompass(num):
    val=int((num/22.5)+.5)
    arr=["N","NNE","NE","ENE","E","ESE", "SE", "SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
    return arr[(val % 16)]

def get_weather_from_weather_com(_ID):
    url = URL.format(LOCATION_ID=_ID, API_key=API_key)
    logger.info("Update Weather with URL: {}".format(url))
    try:
        result = json.loads(urlopen(url).read())
    except URLError as e:
        logger.error("Could not connect to openweathermap.org: {}".format(e))
        return {'error': "Could not connect to openweathermap.org: {}".format(e)}
    return __format_json_result(result)


def __format_json_result(JSON_RESULT):
    #print(json.dumps(JSON_RESULT, indent=4, sort_keys=True))
    logger.info("Parsing JSON Response")
    weather_data = {}
    try:
        #['current_conditions']['icon']
        weather_data.update({'current_conditions':{'icon': ICON_TRANSLATION.get(JSON_RESULT.get("list")[0].get("weather")[0].get("icon"))}})
        #['current_conditions']['temperature']
        weather_data.get('current_conditions').update({'temperature': str(round(JSON_RESULT.get("list")[0].get("main").get("temp"),0))})
        #['current_conditions']['feels_like']
        weather_data.get('current_conditions').update({'feels_like': str(round(JSON_RESULT.get("list")[0].get("main").get("feels_like"),0))})
        #['current_conditions']['wind']['speed']
        weather_data.get('current_conditions').update({'wind': {"speed": str(JSON_RESULT.get("list")[0].get("wind").get("speed"))}})
        #['current_conditions']['wind']['text']    >> Direction
        weather_data.get('current_conditions').get('wind').update({"text": degToCompass(JSON_RESULT.get("list")[0].get("wind").get("deg"))})
        #['forecasts'][0]['sunrise'] >> Sonnenaufgangszeit
        weather_data.update({'forecasts':[{"sunrise": datetime.datetime.fromtimestamp(int(JSON_RESULT.get("city").get("sunrise"))).strftime("%H:%M"),
                                           "night":{},"day":{}},
                                          {"night":{},"day":{}},
                                          {"night":{},"day":{}}]})
        weather_data.get('forecasts')[0].update({"sunset": datetime.datetime.fromtimestamp(int(JSON_RESULT.get("city").get("sunset"))).strftime("%H:%M")})

        today = datetime.date.today()
        clock = datetime.datetime.today()
        if clock.hour <= 11:
            #if it is early at the day. the forecast should show the weather of today (day) and today night.
            DAY0 = today
            DAY1 = today + datetime.timedelta(days=1)
            DAY2 = today + datetime.timedelta(days=2)
        elif 11 < clock.hour <= 20:
            # if it is someware later at the day. the forecast should show the weather of today night.
            # day icon set to the current condition
            obj = JSON_RESULT.get("list")[0]
            timestamp = int(obj.get("dt"))
            if obj.get("rain"):
                weather_data.get('forecasts')[0]["day"].update({"chance_precip": str(obj.get("rain").get("3h"))})
            else:
                weather_data.get('forecasts')[0]["day"].update({"chance_precip": "0"})
            weather_data.get('forecasts')[0]["day"].update({"icon": ICON_TRANSLATION.get(obj.get("weather")[0].get("icon"))})
            weather_data.get('forecasts')[0].update({"high": str(round(obj.get("main").get("temp_max"), 0))})
            weather_data.get('forecasts')[0].update({"day_of_week": datetime.datetime.fromtimestamp(timestamp).strftime("%A")})

            DAY0 = today
            DAY1 = today + datetime.timedelta(days=1)
            DAY2 = today + datetime.timedelta(days=2)

        else:  #clock is > 20
            DAY0 = today + datetime.timedelta(days=1)
            DAY1 = today + datetime.timedelta(days=2)
            DAY2 = today + datetime.timedelta(days=3)

        for obj in JSON_RESULT.get("list"):
            timestamp = int(obj.get("dt"))
            day = datetime.datetime.fromtimestamp(timestamp)
            date = day.date()
            if (date == DAY0) and (day.strftime("%H") in ["21", "22", "23"]):
                ID_NO = 0
                ID_NIGHT_DAY = "night"
            elif (date == DAY0) and (day.strftime("%H") in ["12", "13", "14"]):
                ID_NO = 0
                ID_NIGHT_DAY = "day"
            elif (date == DAY1) and (day.strftime("%H") in ["21", "22", "23"]):
                ID_NO = 1
                ID_NIGHT_DAY = "night"
            elif (date == DAY1) and (day.strftime("%H") in ["12", "13", "14"]):
                ID_NO = 1
                ID_NIGHT_DAY = "day"
            elif (date == DAY2)  and (day.strftime("%H") in ["21", "22", "23"]):
                ID_NO = 2
                ID_NIGHT_DAY = "night"
            elif (date == DAY2)  and (day.strftime("%H") in ["12", "13", "14"]):
                ID_NO = 2
                ID_NIGHT_DAY = "day"
            else: #ignore other
                continue
            # ['forecasts'][0]['day']['chance_precip']     ['forecasts'][0]['night']['chance_precip']
            if obj.get("rain"):
                weather_data.get('forecasts')[ID_NO][ID_NIGHT_DAY].update({"chance_precip": str(obj.get("rain").get("3h"))})
            else:
                weather_data.get('forecasts')[ID_NO][ID_NIGHT_DAY].update({"chance_precip": "0"})
            # ['forecasts'][0]['day']['icon']    ['forecasts'][0]['night']['icon']
            weather_data.get('forecasts')[ID_NO][ID_NIGHT_DAY].update({"icon": ICON_TRANSLATION.get(obj.get("weather")[0].get("icon"))})

            if ID_NIGHT_DAY == "day":
                # ['forecasts'][0]['high']
                weather_data.get('forecasts')[ID_NO].update({"high": str(round(obj.get("main").get("temp_max"), 0))})
                # ['forecasts'][0]['day_of_week'] >> Klartext - Name
                weather_data.get('forecasts')[ID_NO].update({"day_of_week": datetime.datetime.fromtimestamp(timestamp).strftime("%A")})
            else:
                # ['forecasts'][0]['low']
                weather_data.get('forecasts')[ID_NO].update({"low": str(round(obj.get("main").get("temp_min"), 0))})   #night temp
    except Exception as e:
        logger.error("Could not parse response from owm.org: {}".format(e))
        return {'error': "Could not parse response from owm.org: {}".format(e)}
    return weather_data

def get_loc_id_from_weather_com(cityname):
    logger.info("Searching for ID of: {}".format(cityname))
    cityname = cityname.encode('utf-8')
    url = SEARCH_URL.format(SEARCH_STRING=quote(cityname), API_key=API_key)
    #print(url)
    try:
        result = json.loads(urlopen(url).read().lstrip("?(").rstrip(")"))
    except URLError as e:
        return {'error': "Could not connect to openweathermap.org: {}".format(e)}
    #print(json.dumps(result, indent=4, sort_keys=True))
    loc_id_data = {}
    try:
        num_locs = 0
        for target in result["list"]:
            loc_id = target.get("id")  # loc id
            place_name = target.get("name") + ", " +  target.get("sys").get("country")   # place name incl. country
            loc_id_data[num_locs] = (loc_id, place_name)
            num_locs += 1
        loc_id_data['count'] = num_locs
    except IndexError:
        logger.warn('No matching Location IDs found')
        return {'error': 'No matching Location IDs found'}

    return loc_id_data

if __name__ == "__main__":
    from PyQt4.QtCore import QString
    qString = QString("Sattelpeilnstein")
    #qString = QString("München")
    #qString = QString("Cham")
    searchresult = get_loc_id_from_weather_com(unicode(qString))

    if len(searchresult) > 1:  # one is always included (count...)
        for dicts in searchresult:  # populate Index6 with Items
            if dicts == "count":
                continue
            print(searchresult[dicts][1])
            print(searchresult[dicts][0])
            MYID = searchresult[dicts][0]
    else:

        print("No Matches for Hometown: {0}".format(unicode(qString).encode("utf-8")))

    data = get_weather_from_weather_com(MYID)
    print(data)
