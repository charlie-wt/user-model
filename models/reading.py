import base
import story
import variable

class Reading ( base.Base ):
    def __init__ ( self, id, vars, story_id, state, timestamp ):
        self.id = id
        self.vars = vars
        self.story = story_id
        self.state = state
        self.timestamp= timestamp
