import base

class Page (base.Base):
    def __init__ ( self, id, name, functions, conditions ):
        self.id = id
        self.name = name
        self.functions = functions
        self.conditions = conditions
