import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base

class Condition (base.Base):
    def __init__ ( self, id ):
        self.id = id
