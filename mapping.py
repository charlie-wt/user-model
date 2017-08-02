import osrm
import srtm

##### mapping ################
# functions to work out mapping-related stuff, like walk routes & altitude.
##############################

num_requests = 0
routing_client = None
elevation_client = None

def dist ( loc1, loc2, prnt=False ):
# osrm - get walking distance between pages
# note: must be running osrm http backend for this @ localhost:5000 to work
    global routing_client
    if not routing_client:
        routing_client = osrm.Client(host="http://localhost:5000")

    response = routing_client.route(
        coordinates = [[loc1[1], loc1[0]], [loc2[1], loc2[0]]],
        overview = osrm.overview.simplified
    )
    dist = response['routes'][0]['distance']

    if prnt: print('distance from', loc1, 'to', loc2, '=', str(dist)+'m.')
    return dist

def alt ( loc, prnt=False ):
# srtm.py - get altitude of lat/lon
    global elevation_client
    if not elevation_client:
        elevation_client = srtm.get_data()

    ele = elevation_client.get_elevation(loc[0], loc[1])

    if prnt: print("elevation of " + str(loc) + ":", ele)

    return ele
