import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import condition
import ls

class LocationCondition (condition.Condition):
    def __init__ ( self, id, bool, location ):
        self.id = id
        self.type = "location"
        self.bool = bool
        self.location = location

    def check ( self, vars, conds, locs=None, userLoc=None ):
    # Simply return true, since we are only simulating a user that can walk anywhere instantly
        return True

        #if locs == None or userLoc == None: return True

        #location = ls.get(locs, self.location)

        #return this.bool == True and location.withinBounds(userLoc)
