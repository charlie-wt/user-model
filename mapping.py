import osrm
import srtm
import overpy

##### mapping ################
# functions to work out mapping-related stuff, like walk routes & altitude.
##############################

num_requests = 0
routing_client = None
elevation_client = None
poi_client = None

features = {
    'amenity': [
        'bar', 'cafe', 'pub',
#        'college', 'university',
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
#        'palaeontological_site'
    ],
    'historic': [
        'aircraft', 'aqueduct', 'archaeological_site', 'battlefield',
        'boundary_stone', 'cannon', 'castle', 'city_gate',
#        'citywalls',
        'fort',
        'locomotive', 'manor', 'memorial', 'monastery', 'ruins',
#        'rune_stone',
        'ship', 'tomb', 'tower',
#        'wreck'
    ],
    'leisure': [
        'bandstand', 'garden',
#        'marina',
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
# get altitude of lat/lon
    global elevation_client
    if not elevation_client:
        elevation_client = srtm.get_data()

    ele = elevation_client.get_elevation(loc[0], loc[1])

    if prnt: print("elevation of " + str(loc) + ":", ele)

    return ele

def poi ( loc, radius=100, prnt=False ):
# get number of points of interest within some radius of loc.
    global poi_client
    if not poi_client:
        poi_client = overpy.Overpass()

    query = '('
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
#        query += 'rel'+around+feature
    query += ');out;'
    result = poi_client.query(query)

    total = len(result.nodes)+len(result.ways)+len(result.relations)
    if prnt: print(loc, "->", total, "("+ \
                   str(len(result.nodes)), "nodes,",
                   len(result.ways), "ways,",
                   len(result.relations), "relations)")
    return total
