import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base
import ls
import story
import variable

class Reading ( base.Base ):
    def __init__ ( self, id, story, state, timestamp, vars=[] ):
        self.id = id
        self.vars = vars
        self.story = story
        self.state = state
        self.timestamp = timestamp
        self.setUpVariables()

    def setUpVariables ( self ):
        for fn in self.story.functions:
            if fn.type == "increment" or fn.type == "set" or fn.type == "settimestamp":
                ls.save(self.vars, variable.Variable(fn.variable, None))
