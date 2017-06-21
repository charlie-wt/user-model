import condition

class LocationCondition (condition.Condition):
    def __init__ ( self, id, bool, location ):
        self.id = id
        self.type = "location"
        self.bool = bool
        self.location = location

    def check ( self, vars, conds, locs=None, userLoc=None ):
        if loc == None: return True

        location = locs.get(self.location)

        return this.bool == True and location.withinBounds(userLoc)
