import function

class SetFunction (function.Function):
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.type = "set"
        self.conditions = conditions
        self.variable = variable
        self.value = value

    def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
        if (not conditionsPass(vars, conditions, locs, userLoc)) or (not functions): return
        
        var = vars.get(self.variable)
        
        var.value = self.value
        
        vars.save(var)
