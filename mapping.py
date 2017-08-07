import osrm
import srtm

from urllib.request import urlopen
from urllib.error import HTTPError
import json
import time

##### mapping ################
# functions to work out mapping-related stuff, like walk routes & altitude.
##############################

num_requests = 0
routing_client = None
elevation_client = None

features = {
    'amenity': [
        'bar', 'cafe', 'pub',
        'college', 'university',
#        'parking',
        'fountain',
        'clock', 'marketplace', 'place_of_worship'
    ],
    'building': [
        'bridge',
#        'parking'
    ],
    'geological': [
        'outcrop',
        'palaeontological_site'
    ],
    'historic': [
        'aircraft', 'aqueduct', 'archaeological_site', 'battlefield',
        'boundary_stone', 'cannon', 'castle', 'city_gate',
        'citywalls',
        'fort',
        'locomotive', 'manor', 'memorial', 'monastery', 'ruins',
        'rune_stone',
        'ship', 'tomb', 'tower',
        'wreck'
    ],
    'leisure': [
        'bandstand', 'garden',
        'marina',
        'park'
    ],
#    'public_transport': [
#        'stop_position'
#    ],
    'shop': [
        'alcohol', 'beverages'
    ],
    'tourism': [
        'artwork', 'attraction', 'gallery', 'museum'
    ]
}

def dist ( loc1, loc2, prnt=False ):
# get walking distance between pages
# note: must be running osrm http backend @ localhost:5000 for this to work
    global routing_client
    if not routing_client:
        routing_client = osrm.Client(
            host="http://localhost:5000",
            profile='walking'
        )

    response = routing_client.route(
        coordinates = [[loc1[1], loc1[0]], [loc2[1], loc2[0]]],
        overview = osrm.overview.simplified
    )
    dist = response['routes'][0]['distance']

    if prnt: print('distance from', loc1, 'to', loc2, '=', str(dist)+'m.')
    return dist

def alt ( loc, prnt=False ):
# get altitude of lat/lon
    global elevation_client
    if not elevation_client:
        elevation_client = srtm.get_data()

    ele = elevation_client.get_elevation(loc[0], loc[1])

    if prnt: print("elevation of " + str(loc) + ":", ele)

    return ele

def poi ( loc, radius=100, prnt=False ):
# find the number of points of interest from within [radius] of [loc]
    url = "http://overpass-api.de/api/interpreter"
    query = 'data=[out:json];('
    around = '(around:'+str(radius)+','+str(loc[0])+','+str(loc[1])+')'
    for f in features:
        feature = '['+f+'~\"'
        values = ''
        for v in features[f]:
            values += v+'|'
        values = values[:-1]
        feature += values + '\"];'
        query += 'node'+around+feature
        query += 'way'+around+feature
        query += 'rel'+around+feature
    query += ');out count;'

    response = None
    while True:
        try:
            f = urlopen(url, query.encode('utf-8'))
            response = f.read(4096)
            if f.code == 200: break
        except HTTPError:
            print(loc, '- overpass error - retrying in 15 seconds.')
            time.sleep(15)
    f.close()

    json_data = json.loads(response.decode('utf-8'))
    poi = int(json_data['elements'][0]['tags']['total'])

    if prnt: print(loc, '->', poi, 'points of interest.')
    return poi
