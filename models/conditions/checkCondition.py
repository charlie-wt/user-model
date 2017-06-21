import condition

class CheckCondition (condition.Condition):
    def __init__ ( self, id, a, b, aType, bType, operand):
        self.id = id
        self.type = "check"
        self.a = a
        self.b = b
        self.aType = aType
        self.bType = bType
        self.operand = operand
