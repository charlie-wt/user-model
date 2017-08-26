import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import condition
import ls

class LocationCondition (condition.Condition):
    ''' a condition that requires the user to be within a radius of a certain
    location.
    '''
    def __init__ ( self, id, bool, location ):
        self.id = id
        self.type = "location"
        self.bool = bool
        self.location = location

    def check ( self, vars, conds, locs=None, userLoc=None ):
        ''' Simply return true, since we are only simulating a user that can
        walk anywhere instantly.
        '''
        return True
