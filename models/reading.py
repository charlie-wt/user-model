import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))
import time

import base
import ls
import story
import variable

class Reading ( base.Base ):
    ''' a set of variables describing progress through a story. '''
    def __init__ ( self, id, story, state="inprogress", timestamp=time.time(), vars=[] ):
        self.id = id
        self.vars = vars
        self.story = story
        self.state = state
        self.timestamp = timestamp
        self.set_up_variables()

    def set_up_variables ( self ):
        ''' initialse empty variables for a new reading, where needed. '''
        for fn in self.story.functions:
            if fn.type == "increment" or fn.type == "set" or fn.type == "settimestamp":
                ls.save(self.vars, variable.Variable(fn.variable, None))
