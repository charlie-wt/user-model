import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))
sys.path.append(os.path.join(sys.path[0], "../.."))

import base
import ls

class Function (base.Base):
    ''' A function that is executed when the page that holds it is visited.
    Changes variables of the reading, which affects which Conditions pass.
    '''
    def __init__ ( self, id, conditions ):
        self.id = id
        self.conditions = conditions

    def conditions_pass ( self, vars, conditions, locs=None, userLoc=None ):
        ''' find out if the conditions for this function to execute pass. '''
        for c in self.conditions:
            cond = ls.get(conditions, c)
            if not cond.check(vars, conditions, locs, userLoc):
                return False
        return True

    def execute ( self, story, reading, user=None ):
        ''' execute the function. '''
        return
