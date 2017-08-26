import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import condition
import ls

class CheckCondition (condition.Condition):
    ''' a condition that sees whether a variable has a value. '''
    def __init__ ( self, id, variable ):
        self.id = id
        self.type = "check"
        self.variable = variable

    def check ( self, vars, conds, locs=None, userLoc=None ):
        ''' check the condition. '''
        return ls.get(vars, self.variable) != None
