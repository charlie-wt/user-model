import function

class IncrementFunction (function.Function):
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.type = "increment"
        self.conditions = conditions
        self.variable = variable
        self.value = value
