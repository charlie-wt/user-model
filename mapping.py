import sys, os
sys.path.append(os.path.join(sys.path[0], "lib/pyroutelib2"))
sys.path.append(os.path.join(sys.path[0], "models"))

import json
from urllib.parse import urlencode
from urllib.request import urlopen
import route as rt
import location as lc

num_requests = 0
def gdist ( loc1, loc2, prnt=False ):
# get distance between pages, as determined by google maps' routing algorithm.
    origin = str(loc1[0]) + ", " + str(loc1[1])
    destination = str(loc2[0]) + ", " + str(loc2[1])

    url = 'http://maps.googleapis.com/maps/api/directions/json?%s' % urlencode((
          ('origin', origin),
          ('destination', destination),
          ('mode', 'walking')))

    data = json.loads(urlopen(url).read().decode('utf-8'))

    distance = data['routes'][0]['legs'][0]['distance']['value']
    time = data['routes'][0]['legs'][0]['duration']['value']

    global num_requests
    num_requests += 1
    if prnt:
        print(num_requests, ": distance from", origin, "to", destination+" =",
            str(distance)+"m", "("+str(time)+" seconds).")

    return distance

def osmdist ( loc1, loc2, prnt=False ):
# get walking distance between pages, as determined by pyroutelib (osm).
    # load some openstreetmap data
    data = rt.LoadOsm("foot")

    # find nodes from the supplied locations
    node1 = data.findNode(loc1[0], loc1[1])
    node2 = data.findNode(loc2[0], loc2[1])

    if prnt: print("finding distance between", loc1, "and", loc2, " ("+str(lc.metres(loc1, loc2))+"m):")
    # find the route between the nodes
    router = rt.Router(data)
    if loc1 == loc2:
        if prnt: print("distance from", loc1, "to", loc2, "= 0m.")
        return 0
    result, route = router.doRoute(node1, node2)
    if result == "success":
        # get the distance between the nodes
        dist = 0
        for i in range(len(route)-1):
            n1 = data.rnodes[route[i]]
            n2 = data.rnodes[route[i+1]]
            dist += lc.metres((n1[0], n1[1]), (n2[0], n2[1]))
        if prnt: print("distance from", loc1, "to", loc2, "=", str(dist)+"m.")
        return dist
    else:
        print("routing failure:", result)