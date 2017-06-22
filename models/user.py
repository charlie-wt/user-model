import base

class User ( base.Base ):
    def __init__ ( self, id, loc=(50.935659, 1.396098) ):
        self.id = id
        self.loc = loc
