import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import time

import condition
import ls

class TimePassedCondition (condition.Condition):
    def __init__ ( self, id, variable, minutes ):
        self.id = id
        self.type = "timepassed"
        self.variable = variable
        self.minutes = minutes

    def check ( self, vars, conds, locs=None, userLoc=None ):
    # check the condition
    # TODO - as yet untested
    # TODO - should probably just return True, as with locationConditions.
        ts = ls.get(vars, self.variable)

        now = time.time()
        timestamp = int(ts.value)

        earliest = timestamp + now

        return earliest < now
