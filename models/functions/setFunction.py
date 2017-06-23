import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import function
import ls

class SetFunction (function.Function):
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.type = "set"
        self.conditions = conditions
        self.variable = variable
        self.value = value

    def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
        if (not self.conditions_pass(vars, conditions, locs, userLoc)) or (not functions): return

        var = ls.get(vars, self.variable)

        var.value = self.value

        ls.save(vars, var)
