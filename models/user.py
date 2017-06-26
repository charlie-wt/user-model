import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base
import ls
import page

class User ( base.Base ):
    def __init__ ( self, id, loc=(50.935659, -1.396098) ):
        self.id = id
        self.loc = loc
        self.path = []

    def page ( self ):
        return self.path[len(self.path)-1] if len(self.path) > 0 else None

    def move ( self, id, pages, story, reading ):
        # move to a new page
        self.path.append(pages[id])

        # update player's location (lat, lon) to that of new page, if applicable
        page_loc = self.page().getLoc(story)
        if page_loc is not None:
            self.loc = (page_loc[0], page_loc[1])

        # execute new page's function
        self.page().execute_functions(story, reading, self)

        # return new list of visible pages
        return page.update_all(story.pages, story, reading, self)

    def lat ( self ):
    # simple helper
        return self.loc[0]

    def lon ( self ):
    # simple helper
        return self.loc[1]
