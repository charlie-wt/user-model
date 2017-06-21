import function

class SetFunction (function.Function):
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.type = "set"
        self.conditions = conditions
        self.variable = variable
        self.value = value
