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

def galt ( loc, prnt=False ):
# google maps api - get altitude of a lat/lon
    strloc = str(loc[0]) + "," + str(loc[1])

    url = 'http://maps.googleapis.com/maps/api/elevation/json?%s' % urlencode({
            'locations': strloc })

    data = json.loads(urlopen(url).read().decode('utf-8'))
    alt = data['results'][0]['elevation']

    global num_requests
    num_requests += 1
    if prnt:
        print(num_requests, ": elevation of", loc, "is", alt)

    return alt

def dstkalt ( loc, prnt=False ):
# datasciencetoolkit api - get altitude of a lat/lon
    sloc = str(loc[0]) + "%2c" + str(loc[1])

    url = 'http://www.datasciencetoolkit.org/coordinates2statistics/' \
            +sloc+'?statistics=elevation'
    data = json.loads(urlopen(url).read().decode('utf-8'))
    alt = data[0]['statistics']['elevation']['value']

    if prnt:
        print("elevation of", loc, "is", alt)

    return alt

def srtmalt ( loc, prnt=False ):
# srtm.py - get altitude of lat/lon
    global elevation_client
    if not elevation_client:
        elevation_client = srtm.get_data()

    ele = elevation_client.get_elevation(loc[0], loc[1])

    if prnt: print("elevation of " + str(loc) + ":", ele)

    return ele
