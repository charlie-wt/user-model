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

    #def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
    def execute ( self, story, reading, userLoc=None ):
        if (not self.conditions_pass(reading.vars, story.conditions, story.locations, userLoc)) or (not story.functions): return
        
        for f in self.functions:
            fun = ls.get(story.functions, f)
            fun.execute(story, reading, userLoc)
