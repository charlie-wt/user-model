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

    def execute ( self, story, reading, user=None ):
        if not self.conditions_pass(reading.vars, story.conditions, story.locations, user.loc): return

        var = ls.get(reading.vars, self.variable)
        var.value = int(var.value) + int(self.value)
        ls.save(reading.vars, var)
