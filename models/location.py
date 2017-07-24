import math

import base

class Location (base.Base):
    def __init__ ( self, id, type, lat, lon, radius ):
        self.id = id
        self.type = type
        self.lat = lat
        self.lon = lon
        self.radius = radius

    def withinBounds ( self, loc ):
        return metres((self.lat, self.lon), (loc.lat, loc.lon)) < self.radius

def metres ( loc1, loc2 ):
    # distance in metres between two lat/lon coordinates
    r = 12742000  # earth's diameter
    dLat = deg2rad(loc2[0] - loc1[0])
    dLon = deg2rad(loc2[1] - loc1[1])

    dLatSin = math.sin(dLat / 2)
    dLonSin = math.sin(dLon / 2)

    a = dLatSin**2 + math.cos(deg2rad(loc1[0])) * math.cos(deg2rad(loc2[0])) * dLonSin**2

    return r * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def deg2rad ( deg ):
    return deg * 0.01745329251994329576923690768489
