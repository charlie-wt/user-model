import condition

class TimeRangeCondition (condition.Condition):
    def __init__ ( self, id, variable, start, end ):
        self.id = id
        self.type = "timerange"
        self.variable = variable
        self.start = start
        self.end = end
