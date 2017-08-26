import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base
import ls
import page

class User ( base.Base ):
    ''' A user to read stories. Has a location, and the pages they've been to.
    not strictly necessary for the simulation system, but kept for completeness.
    '''
    def __init__ ( self, id, loc=(50.935659, -1.396098) ):
        self.id = id
        self.loc = loc
        self.path = []

    def page ( self ):
        ''' return the user's current page. '''
        return self.path[-1] if self.path else None

    def move ( self, page_id, pages, story, reading ):
        ''' move to a new page. '''
        self.path.append(pages[page_id])

        # update player's location (lat, lon) to that of new page, if applicable
        page_loc = self.page().get_loc(story)
        if page_loc is not None:
            self.loc = page_loc

        # execute new page's function
        self.page().execute_functions(story, reading, self)

        # return new list of visible pages
        return page.update_all(story.pages, story, reading, self)

    def lat ( self ):
        ''' simple helper. '''
        return self.loc[0]

    def lon ( self ):
        ''' simple helper. '''
        return self.loc[1]
