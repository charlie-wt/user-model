import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base

class Function (base.Base):
    def __init__ ( self, id, conditions, variable, value ):
        self.id = id
        self.conditions = conditions
