import function

class ChainFunction (function.Function):
    def __init__ ( self, id, conditions, functions ):
        self.id = id
        self.type = "chain"
        self.conditions = conditions
        self.functions = functions
