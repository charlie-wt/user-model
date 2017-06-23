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

    def execute ( self, story, reading, userLoc=None ):
        if (not self.conditions_pass(reading.vars, story.conditions, story.locations, userLoc)) or (not story.functions): return
        
        var = ls.get(reading.vars, variable)
        
        curr_val = int(var.value)
        new_val = curr_val + self.value
        
        var.value = str(new_val)

        ls.save(reading.vars, var)
