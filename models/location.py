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
        return metres(self.lat, self.lon, loc.lat, loc.lon) < self.radius

    @staticmethod
    def metres ( lat1, lon1, lat2, lon2 ):
        r = 12742000
        dLat = Location.deg2rad(lat2 - lat1)
        dLon = Location.deg2rad(lon2 - lon1)

        dLatSin = math.sin(dLat / 2)
        dLonSin = math.sin(dLon / 2)

        a = dLatSin**2 + math.cos(Location.deg2rad(lat1)) * math.cos(Location.deg2rad(lat2)) * dLonSin**2

        return r * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def deg2rad ( deg ):
        return deg * 0.01745329251994329576923690768489
