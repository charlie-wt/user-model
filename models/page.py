import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base
import ls

class Page (base.Base):
    def __init__ ( self, id, name, functions, conditions ):
        self.id = id
        self.name = name
        self.functions = functions
        self.conditions = conditions
        self.visible = False

    def update ( self, vars, conds, locs, userLoc ):
    # see if this page should be visible
        for c in self.conditions:
            if not ls.get(conds, c).check(vars, conds):
                self.visible = False
                return
        self.visible = True

    def execute_functions ( self, story_id, reading_id, vars, conds, locs, userLoc, functions ):
    # execute all the functions on this page
        for f in this.functions:
            ls.get(functions, f).execute(story_id, reading_id, vars, conds, functions, locs, userLoc)
