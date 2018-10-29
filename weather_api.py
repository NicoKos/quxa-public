#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
# QUXA is a QUIC User eXperience Assesment experiment tool
#
# Copyright © 2018 CNES
#
# This file is part of the OpenBACH testbed.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY, without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see http://www.gnu.org/licenses/.


"""Weather API program"""
__author__ = 'Ludovic Thomas'

##################### CONFIG ######################
# Please complete the following parameters

#The API adress
target = "https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/airports/weather/current-conditions-list"
#API configuration : please provide the key, the ICAO code of the nearest airport, and format
api_config = [
    ["api_key","my-weather-api-key"],                       #Provide you own api key. Visit https://www.icao.int/safety/istars/pages/api-data-service.aspx
    ["airports","LFBO"],                                    #LFBO is Toulouse Blagnac (France) airport. Change with your own code
    ["states",""],                                          #This field can be kept empty
    ["format","json"]                                       #Output format json
]

################### END CONFIG ####################


import urllib.request

class WeatherChecker(object):
    #Initialize class
    def __init__(self, outFolder, date_string):
        self.outFolder = outFolder
        self.date_string = date_string
        #Build HTTP request
        temp_request = target
        temp_request += "?"
        for i in range(len(api_config)):
            temp_request += api_config[i][0] + "=" + api_config[i][1] + "&"
        #Remove last "&"
        temp_request = temp_request[:-1]
        self.request = temp_request
        #Building output file
        self.outPutFileName = outFolder + "weather_" + date_string + ".json"
    def requestWeather(self):
        "Perform the request"
        print("[Weather] Requesting weather of " + api_config[1][1] + " ...", end="", flush=True)
        content = urllib.request.urlopen(self.request).read()
        print("Done")
        print("[Weather] Writing down results ...", end="", flush=True)
        file = open(self.outPutFileName,'wb')
        file.write(content)
        file.close()
        print("Done")
if __name__ == '__main__':
    myWeather = WeatherChecker("/tmp/", "test")
    myWeather.requestWeather()

