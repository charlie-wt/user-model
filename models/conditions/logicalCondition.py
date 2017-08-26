import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import condition
import ls

class LogicalCondition (condition.Condition):
    ''' a condition that evaluates two variables with a logical operator (AND,
    OR).
    '''
    def __init__ ( self, id, operand, conditions ):
        self.id = id
        self.type = "logical"
        self.operand = operand
        self.conditions = conditions

    def check ( self, vars, conds, locs=None, userLoc=None ):
        ''' check the condition. '''
        if self.operand == "AND":
            for c in self.conditions:
                if not ls.get(conds, c).check(vars, conds, locs, userLoc): return False
            return True

        if self.operand == "OR":
            for c in self.conditions:
                if ls.get(conds, c).check(vars, conds, locs, userLoc): return True
            return False
