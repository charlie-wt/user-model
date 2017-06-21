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
        return math.sqrt((self.lat-loc.lat)**2 + (self.lon-loc.lat)**2) <= radius
