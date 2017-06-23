import sys, os
sys.path.append(os.path.join(sys.path[0], ".."))

import base
import ls

class Page (base.Base):
    def __init__ ( self, id, name, functions, conditions ):
        self.id = id
        self.name = name
        self.functions = functions
        self.conditions = conditions
        self.visible = False

    def update ( self, story, reading, user ):
    # see if this page should be visible
        for c in self.conditions:
            print(c, "=", ls.get(story.conditions, c).check(reading.vars, story.conditions))
            if not ls.get(story.conditions, c).check(reading.vars, story.conditions):
                self.visible = False
                return
        self.visible = True

    def execute_functions ( self, story, reading, user ):
    # execute all the functions on this page
        for f in self.functions:
            ls.get(story.functions, f).execute(story, reading, user)

def update_all ( pages, story, reading, user ):
# update a bunch of pages at once
    visible = []
    for page in pages:
        page.update( story, reading, user )
        if page.visible: visible.append(page)
    return visible
