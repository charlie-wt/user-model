import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import condition
import coll as ls

class LogicalCondition (condition.Condition):
    def __init__ ( self, id, operand, conditions ):
        self.id = id
        self.type = "logical"
        self.operand = operand
        self.conditions = conditions
    
    def check ( self, vars, conds, locs=None, userLoc=None ):
    # check the condition
        if self.operand == "AND":
            for c in self.conditions:
                if not ls.get(conds, c).check(vars, conds, locs, userLoc): return False
            return True
        
        if self.operand == "OR":
            for c in self.conditions:
                if ls.get(conds, c).check(vars, conds, locs, userLoc): return True
            return False
