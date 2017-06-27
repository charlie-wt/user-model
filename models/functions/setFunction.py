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

    def execute ( self, story, reading, user=None ):
        if not self.conditions_pass(reading.vars, story.conditions, story.locations, user.loc): return

        var = ls.get(reading.vars, self.variable)

        print("setting", var.id, "to", self.value, "(", type(self.value), ")")
        var.value = self.value

        ls.save(reading.vars, var)
