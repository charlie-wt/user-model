import base

class Story (base.Base):
    def __init__ ( self, id, name, pages, conditions, functions, locations ):
        self.id = id
        self.name = name
        self.pages = pages
        self.conditions = conditions
        self.functions = functions
        self.locations = locations
