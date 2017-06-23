import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import time

import function
import ls

class SetTimestampFunction (function.Function):
    def __init__ ( self, id, conditions, variable ):
        self.id = id
        self.type = "settimestamp"
        self.conditions = conditions
        self.variable = variable

    def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
        if (not self.conditions_pass(vars, conditions, locs, userLoc)) or (not functions): return
        
        var = ls.get(vars, self.var)
        
        var.value = str(time.time())
        ls.save(vars, var)
