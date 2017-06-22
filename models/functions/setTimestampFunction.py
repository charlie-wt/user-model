import time

import function

class SetTimestampFunction (function.Function):
    def __init__ ( self, id, conditions, variable ):
        self.id = id
        self.type = "settimestamp"
        self.conditions = conditions
        self.variable = variable

    def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
        if (not conditions_pass(vars, conditions, locs, userLoc)) or (not functions): return
        
        var = vars.get(self.var)
        
        var.value = str(time.time())
        vars.save(var)
