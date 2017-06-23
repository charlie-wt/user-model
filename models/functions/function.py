import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))
sys.path.append(os.path.join(sys.path[0], "../.."))

import base
import ls

class Function (base.Base):
    def __init__ ( self, id, conditions ):
        self.id = id
        self.conditions = conditions

    def conditions_pass ( self, vars, conditions, locs=None, userLoc=None ):
        for c in self.conditions:
            cond = ls.get(conditions, c)
            if not cond.check(vars, conditions, locs, userLoc): return False
        return True

    #def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
    def execute ( self, story, reading, userLoc=None ):
        return
