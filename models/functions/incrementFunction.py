import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import function
import ls

class IncrementFunction (function.Function):
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.type = "increment"
        self.conditions = conditions
        self.variable = variable
        self.value = value

    def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
        if (not conditions_pass(vars, conditions, locs, userLoc)) or (not functions): return
        
        var = ls.get(vars, variable)
        
        curr_val = int(var.value)
        new_val = curr_val + self.value
        
        var.value = str(new_val)

        ls.save(vars, var)
