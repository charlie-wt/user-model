import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base

class Condition (base.Base):
    ''' A condition that can be held by a page or function. Pages need all their
    conditions to pass in order to be visible. Functions need all their
    conditions to pass in order to execute.
    '''
    def __init__ ( self, id ):
        self.id = id

    def check ( self, vars, loc=None ):
        ''' check the condition -- to be overloaded. '''
        return False
