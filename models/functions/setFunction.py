import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import function
import ls

class SetFunction (function.Function):
    ''' a function that sets a variable to be equal to a certain amount. '''
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.type = "set"
        self.conditions = conditions
        self.variable = variable
        self.value = value

    def execute ( self, story, reading, user=None ):
        ''' execute the function. '''
        if not self.conditions_pass(reading.vars, story.conditions, story.locations, user.loc): return

        var = ls.get(reading.vars, self.variable)
        var.value = self.value
        ls.save(reading.vars, var)
