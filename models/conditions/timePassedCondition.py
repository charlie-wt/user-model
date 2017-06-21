import condition

class TimePassedCondition (condition.Condition):
    def __init__ ( self, id, variable, minutes ):
        self.id = id
        self.type = "timepassed"
        self.variable = variable
        self.minutes = minutes
