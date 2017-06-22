import function

class IncrementFunction (function.Function):
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.type = "increment"
        self.conditions = conditions
        self.variable = variable
        self.value = value

    def execute ( self, story_id, reading_id, vars, conditions, functions, locs=None, userLoc=None ):
        if (not conditionsPass(vars, conditions, locs, userLoc)) or (not functions): return
        
        var = vars.get(variable)
        
        curr_val = int(var.value)
        new_val = curr_val + self.value
        
        var.value = str(new_val)

        vars.save(var)
