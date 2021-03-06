import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import time

import function
import ls

class SetTimestampFunction (function.Function):
    ''' a function that sets a variable to be equal to the current time. '''
    def __init__ ( self, id, conditions, variable ):
        self.id = id
        self.type = "settimestamp"
        self.conditions = conditions
        self.variable = variable

    def execute ( self, story, reading, user=None ):
        ''' execute the function. '''
        if not self.conditions_pass(reading.vars, story.conditions, story.locations, user.loc): return

        var = ls.get(reading.vars, self.var)
        var.value = str(time.time())
        ls.save(reading.vars, var)
