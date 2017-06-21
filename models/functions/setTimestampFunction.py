import function

class SetTimestampFunction (function.Function):
    def __init__ ( self, id, conditions, variable ):
        self.id = id
        self.type = "settimestamp"
        self.conditions = conditions
        self.variable = variable
