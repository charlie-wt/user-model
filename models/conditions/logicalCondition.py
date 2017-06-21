import condition

class LogicalCondition (condition.Condition):
    def __init__ ( self, id, operand, conditions ):
        self.id = id
        self.type = "logical"
        self.operand = operand
        self.conditions = conditions
