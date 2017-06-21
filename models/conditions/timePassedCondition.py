import time

import condition

class TimePassedCondition (condition.Condition):
    def __init__ ( self, id, variable, minutes ):
        self.id = id
        self.type = "timepassed"
        self.variable = variable
        self.minutes = minutes
        
    def check ( self, vars, conds, locs=None, userLoc=None ):
    # check the condition
    # TODO - as yet untested
        ts = vars.get(self.variable)
        
        now = time.time()
        timestamp = int(ts.value)
        
        earliest = timestamp + now
        
        return earliest < now
