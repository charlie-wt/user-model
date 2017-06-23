import sys, os
sys.path.append(os.path.join(sys.path[0], "../.."))

import condition
import ls

class ComparisonCondition (condition.Condition):
    def __init__ ( self, id, a, b, aType, bType, operand):
        self.id = id
        self.type = "comparison"
        self.a = a
        self.b = b
        self.aType = aType
        self.bType = bType
        self.operand = operand
    
    def check ( self, vars, conds, locs=None, userLoc=None ):
    # check the condition
        a = self.value(self.a, self.aType, vars)
        b = self.value(self.b, self.bType, vars)
        
        if   self.operand == "==":
            return a == b
        elif self.operand == "!=":
            return a != b
        elif self.operand == "<":
            return a < b
        elif self.operand == ">":
            return a > b
        elif self.operand == "<=":
            return a <= b
        elif self.operand == ">=":
            return a >= b

    def value ( self, value, type, vars ):
    # get the value of a / b
        if type == "Variable":
            variable = ls.get(vars, value)
            return variable.value if variable else None
        if type == "Integer":
            return int(value)
        return value
