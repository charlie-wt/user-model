##### record #################
# contains more full state info for when walking through a story than just a
# list of the pages visited.
# info:
#     options: a dictionary containing page : probability, expressing the chance
#              of choosing that page from the current self.page
##############################

class Record:
    def __init__ ( self, page, options, visible=None ):
        self.page = page
        self.options = options
        if visible is not None: fill_options(self.options, visible)

def fill_options ( options, visible ):
# add to the options dictionary nodes that are visible, but have never been
# visited in the logs.
    for p in visible:
        if p not in options:
            options[p] = 0

def add ( store, page, options, visible=None ):
    it = Record(page, options, visible)
    store.append(it)
    return it
