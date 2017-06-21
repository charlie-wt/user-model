import condition

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
                if not c.execute(vars, conds, locs, userLoc): return False
            return True
        
        if self.operand == "OR":
            for c in self.conditions:
                if c.execute(vars, conds, locs, userLoc): return True
            return False
