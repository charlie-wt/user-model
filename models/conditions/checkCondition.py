import condition

class CheckCondition (condition.Condition):
    def __init__ ( self, id, variable ):
        self.id = id
        self.type = "check"
        self.variable = variable

    def check ( self, vars, conds, locs=None, userLoc=None ):
    # check the condition
        return vars.get(self.variable) != None
