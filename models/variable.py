import base

class Variable (base.Base):
    ''' Holds a value, that can be changed by functions. '''
    def __init__ ( self, id, value ):
        self.id = id
        self.value = value
