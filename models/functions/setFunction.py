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

    #def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
    def execute ( self, story, reading, userLoc=None ):
        if (not self.conditions_pass(reading.vars, story.conditions, story.locations, userLoc)) or (not story.functions): return

        var = ls.get(reading.vars, self.variable)

        var.value = self.value

        ls.save(reading.vars, var)
