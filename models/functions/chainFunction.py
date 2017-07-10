import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import function
import ls

class ChainFunction (function.Function):
    def __init__ ( self, id, conditions, functions ):
        self.id = id
        self.type = "chain"
        self.conditions = conditions
        self.functions = functions

    def execute ( self, story, reading, user=None ):
        if not self.conditions_pass(reading.vars, story.conditions, story.locations, user.loc): return
        if not self.functions: return

        for f in self.functions:
            fn = ls.get(story.functions, f)
            fn.execute(story, reading, user)
