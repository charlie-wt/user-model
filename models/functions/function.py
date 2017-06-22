import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base

class Function (base.Base):
    def __init__ ( self, id, conditions ):
        self.id = id
        self.conditions = conditions
    
    def conditions_pass ( self, vars, conditions, locs=None, userLoc=None ):
        for c in self.conditions:
            cond = conditions.get(c.id)
            if not cond.check(vars, conditions, locs, userLoc): return False
        return True
    
    def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
        return
