import condition

class LocationCondition (condition.Condition):
    def __init__ ( self, id, bool, location ):
        self.id = id
        self.type = "location"
        self.bool = bool
        self.location = location
