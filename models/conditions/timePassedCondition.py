import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import time

import condition
import ls

class TimePassedCondition (condition.Condition):
    ''' a condition that checks whether enough time has passed since a
    variable was set.
    '''
    def __init__ ( self, id, variable, minutes ):
        self.id = id
        self.type = "timepassed"
        self.variable = variable
        self.minutes = minutes

    def check ( self, vars, conds, locs=None, userLoc=None ):
        ''' check the condition '''
        return True

#        # TODO - as yet untested
#        ts = ls.get(vars, self.variable)
#
#        now = time.time()
#        timestamp = int(ts.value)
#
#        earliest = timestamp + now
#
#        return earliest < now
