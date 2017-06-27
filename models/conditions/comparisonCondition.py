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
        if self.operand == "<" or self.operand == ">":
            print("a =", a, ":", self.aType, "(", type(a), ")")
            print("b =", b, ":", self.bType, "(", type(b), ")")

        # in js, ( int <comparator> undefined ) = false. in Python, it throws an error.
        if (a is None and type(b) is int) or (b is None and type(a) is int):
            return False

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
        if type == "String":
            return value == "true" if value == "true" or value == "false" else value
        return value
