import csv
from gmplot import gmplot
import json
from pprint import pprint
import urllib.request  as urllib2 
import os
import time
import math
import random

key = "RzxaJBZ093ilm9BRpsuMWX8AiYTmc8kN"
EARTH_POLAR_RADIUS_METER = 6356800
EARTH_EQUATORIAL_RADIUS_METER = 6378100
meterWidth = 1000
count = 50

def queryEventfulWithId(id):
	url = "http://api.eventful.com/json/events/get?app_key=srG2DMrq4VpRxGvw&id="+id
	response = urllib2.urlopen(url).read()
	rspJSON = json.loads(response)
	return rspJSON
    
# Gets the metric length corresponding to the latitude, in degrees.
def getLatitudeWidth(meterWidth):
    return meterWidth/(2*math.pi*EARTH_POLAR_RADIUS_METER ) *360

# Convert the metric width to the corresponding longitude width at latitude
def getLongitudeWidthAtLatitue(latitude, meterWidth):
    circleMeterLengthAtLatitude = 2 * math.pi * EARTH_EQUATORIAL_RADIUS_METER * math.cos(latitude / 180 * math.pi)
    return meterWidth/circleMeterLengthAtLatitude * 360

def degreesToRadians(degrees):
	return degrees * math.pi / 180

def distanceInMetersBetweenEarthCoordinates(lat1, lon1, lat2, lon2):
	earthRadiusKm = 6371
	dLat = degreesToRadians(lat2-lat1)
	dLon = degreesToRadians(lon2-lon1)
	lat1 = degreesToRadians(lat1)
	lat2 = degreesToRadians(lat2)
	a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2) 
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)) 
	return earthRadiusKm * c * 1000


# Generates a uniform distribution of count coordinates
# Boundary defined by lat,lon of center corner and width in meters
def generateCoordsWithinSquare(centerLat,centerLon,meterWidth,count,gmap,map_file):

	# Generate rectangle width in latitude and longitude coordinates
	dLat = getLatitudeWidth(meterWidth)
	dLon = getLongitudeWidthAtLatitue(centerLat,meterWidth)

	# Generate and show rectangle boundaries
	upperLeftLat = centerLat + (dLat / 2.0)
	upperLeftLon = centerLon - (dLon / 2.0)

	lowerRightLat = upperLeftLat - dLat
	lowerRightLon = upperLeftLon + dLon

	upperRightLat = upperLeftLat
	upperRightLon = lowerRightLon

	lowerLeftLat = lowerRightLat
	lowerLeftLon = upperLeftLon

	latitudes = []
	longitudes = []
	distances_to_center = []

	# Generate count randomly distributed coordinates
	for i in range(count):
		lat = random.uniform(upperLeftLat, lowerLeftLat)
		lon = random.uniform(upperLeftLon, upperRightLon)
		dist = distanceInMetersBetweenEarthCoordinates(centerLat,centerLon,lat,lon)
		latitudes.append(lat)
		longitudes.append(lon)
		distances_to_center.append(dist)
        
	boundaries = [[upperLeftLat, upperRightLat, lowerRightLat, lowerLeftLat, upperLeftLat], [upperLeftLon, upperRightLon, lowerRightLon, lowerLeftLon, upperLeftLon]]

	return latitudes,longitudes,distances_to_center

def getSpeedAtLoc(lat,lon):
    try:
        url = "https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?key="+key+"&point="+lat+","+lon+"&unit=MPH"
        response = urllib2.urlopen(url).read()
        rspJSON = json.loads(response)
        data = rspJSON['flowSegmentData']
        freeFlowSpeed = data["freeFlowSpeed"]
        currentSpeed = data["currentSpeed"]
        confidence = data["confidence"]
        ratio = round(currentSpeed/float(freeFlowSpeed),2)

        #TODO: put average of returned segments lat and lon here

        return [str(lat),str(lon),str(freeFlowSpeed),str(currentSpeed),str(ratio),str(confidence),str(time.time())]
    except urllib2.HTTPError as err:
        print ("not found")

#Event IDs for Dates
March22 = ['E0-001-112125565-5','E0-001-110726616-9','E0-001-112445339-1','E0-001-105077404-7','E0-001-111610388-0','E0-001-113022738-0','E0-001-113021529-7']
# March23 = ['E0-001-112893006-5','E0-001-112323987-3','E0-001-110961124-8']
March23 = ['E0-001-112893006-5']
March24 = ['E0-001-105545550-9','E0-001-103317913-9','E0-001-111103613-0','E0-001-104932362-5']
March25 = ['E0-001-112609175-1','E0-001-111148684-9']
March26 = ['E0-001-112887201-7']
March27 = ['E0-001-095606083-4','E0-001-112228617-5']
March31 = ['E0-001-110902509-8','E0-001-109288741-1','E0-001-103166627-9']
April1 = ['E0-001-111784050-8']

import pandas as pd
columns = ['event','title','venue','venue_lat','venue_lon','sample_lats','sample_lons','sample_dist']
df = pd.DataFrame(columns=columns)


for i in March23:
    event = queryEventfulWithId(i)
    venue_name = event["venue_name"]
    directory = "Venues/"+venue_name
    latitude = float(event["latitude"])
    longitude = float(event["longitude"])
    gmap = gmplot.GoogleMapPlotter(latitude, longitude, 16)
    map_file = directory+"/map.html"
    latitudes50,longitudes50,distances_to_center = generateCoordsWithinSquare(latitude,longitude,meterWidth,count,gmap,map_file)
    df.loc[i] = [event,event['title'],venue_name,latitude,longitude,latitudes50,longitudes50,distances_to_center]

df.to_csv('March23_' + venue_name + '.csv')

counter = 0
while counter <= 11:
	columns1 = ['eventname','loc_type','lat','lon','freeflowspeed','currentspeed','ratio','confidence','CST Time','dist_from_center']
	i = 0
	dfadd = pd.DataFrame([['ignore this row',"2",1.1,1.1,21,21,1,1,1,0]],columns=columns1)

	#CHANGE THE DATE BELOW TO March23/March24 etc based on today's date

	for i in range(0,len(March23)):
	    loc_type = "C"
	    lat = df['venue_lat'][i]
	    lon = df['venue_lon'][i]
	    lat,lon,freeFlowSpeed,currentSpeed,ratio,confidence,timeticks = getSpeedAtLoc(str(lat),str(lon))
	    dfadd.loc[len(dfadd)]= [str(df['title'][i]),loc_type,lat,lon,freeFlowSpeed,currentSpeed,ratio,confidence,time.ctime(int(float((timeticks)))),0]

	    for j in range(50):
	        loc_type = "S"
	        lat,lon,freeFlowSpeed,currentSpeed,ratio,confidence,timeticks = getSpeedAtLoc(str(df['sample_lats'][i][j]),str(df['sample_lons'][i][j]))
	        dfadd.loc[len(dfadd)] = [str(df['title'][i]),loc_type,lat,lon,freeFlowSpeed,currentSpeed,ratio,confidence,time.ctime(int(float((timeticks)))),df['sample_dist'][i][j]]
	
	dfadd.to_csv('March23_' + venue_name + str(time.ctime(int(float((timeticks))))) + '.csv')
	if counter == 11:
		break
	time.sleep(1800)
	counter += 1
