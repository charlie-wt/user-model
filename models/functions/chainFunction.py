import function

class ChainFunction (function.Function):
    def __init__ ( self, id, conditions, functions ):
        self.id = id
        self.type = "set"
        self.conditions = conditions
        self.functions = functions
